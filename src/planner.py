# this file builds and saves the cleaned student course status dataset.

from pathlib import Path

import pandas as pd

# support package imports and direct execution from the project root.
try:
    from src.load_data import (
        COURSE_COLUMNS,
        COURSE_HISTORY_KEYS,
        REQUIRED_FILES,
        load_csv_file,
    )
    from src.utils import build_course_code, clean_course_number, clean_student_id
except ModuleNotFoundError:
    from load_data import (
        COURSE_COLUMNS,
        COURSE_HISTORY_KEYS,
        REQUIRED_FILES,
        load_csv_file,
    )
    from utils import build_course_code, clean_course_number, clean_student_id


OUTPUT_COLUMNS = [
    "student_id",
    "course_code",
    "course_prefix",
    "course_number",
    "course_title",
    "semester",
    "credits",
    "grade_mode",
    "passing_status",
    "status",
    "source_file",
]


def normalize_passing_status(value):
    # translate source status codes into labels used by the planning dataset.
    if pd.isna(value):
        return "unknown"

    status_code = str(value).strip().lower()
    status_labels = {
        "c": "complete",
        "ip": "in_progress",
    }
    return status_labels.get(status_code, "unknown")


def _get_passing_value(course_frame):
    # use an override only when the primary passing value is empty.
    passing = course_frame["Passing"].fillna("").astype(str).str.strip()

    if "Passing Override" not in course_frame.columns:
        return passing

    override = course_frame["Passing Override"].fillna("").astype(str).str.strip()
    return passing.where(passing.ne(""), override)


def build_student_course_status(data):
    # reshape each course export into the shared intermediate schema.
    course_frames = []

    for data_key in COURSE_HISTORY_KEYS:
        if data_key not in data:
            raise ValueError(f"missing course dataframe: {data_key}")

        source = data[data_key].copy()
        required_columns = [
            "UID",
            "Prefix",
            "Number",
            "Course Title",
            "Semester",
            "Credits",
            "Grade Mode",
            "Passing",
        ]
        missing_columns = [
            column for column in required_columns if column not in source.columns
        ]
        if missing_columns:
            raise ValueError(
                f"{data_key}: missing columns {', '.join(missing_columns)}"
            )

        passing_values = _get_passing_value(source)
        course_frame = pd.DataFrame(
            {
                "student_id": source["UID"].map(clean_student_id),
                "course_code": [
                    build_course_code(prefix, number)
                    for prefix, number in zip(source["Prefix"], source["Number"])
                ],
                "course_prefix": (
                    source["Prefix"].fillna("").astype(str).str.strip().str.upper()
                ),
                "course_number": source["Number"].map(clean_course_number),
                "course_title": source["Course Title"].fillna("").astype(str).str.strip(),
                "semester": source["Semester"].fillna("").astype(str).str.strip(),
                "credits": source["Credits"],
                "grade_mode": source["Grade Mode"].fillna("").astype(str).str.strip(),
                "passing_status": passing_values.str.lower(),
                "status": passing_values.map(normalize_passing_status),
                "source_file": REQUIRED_FILES[data_key],
            }
        )
        course_frames.append(course_frame)

    return pd.concat(course_frames, ignore_index=True)[OUTPUT_COLUMNS]


def save_student_course_status(data, output_path=None):
    # create the intermediate folder and save the combined course records.
    default_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "intermediate"
        / "student_course_status.csv"
    )
    destination = Path(output_path) if output_path is not None else default_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    course_status = build_student_course_status(data)
    course_status.to_csv(destination, index=False)
    return destination


def _load_course_history():
    # load only the four raw exports needed to build this intermediate file.
    raw_data_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
    data = {}

    for data_key in COURSE_HISTORY_KEYS:
        file_path = raw_data_dir / REQUIRED_FILES[data_key]
        if not file_path.exists():
            raise FileNotFoundError(f"missing required file: {file_path}")

        course_frame = load_csv_file(file_path)
        missing_columns = [
            column for column in COURSE_COLUMNS if column not in course_frame.columns
        ]
        if missing_columns:
            raise ValueError(
                f"{data_key}: missing columns {', '.join(missing_columns)}"
            )
        data[data_key] = course_frame

    return data


if __name__ == "__main__":
    # run the first intermediate data step from the project root.
    loaded_data = _load_course_history()
    saved_path = save_student_course_status(loaded_data)
    row_count = len(build_student_course_status(loaded_data))
    print(f"saved {row_count} rows to {saved_path}")
