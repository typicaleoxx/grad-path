# this file loads raw grad path csv files and validates the columns needed downstream.

from pathlib import Path

import pandas as pd

from src.utils import build_course_code


REQUIRED_FILES = {
    "theatre_majors": "Train01_TheatreMajors.csv",
    "the_courses": "Train01_THE_Courses.csv",
    "tpa_courses": "Train01_TPA_Courses.csv",
    "tpp_courses": "Train01_TPP_Courses.csv",
    "practicum_courses": "Train01_Practicum_Courses.csv",
    "degree_requirements": "degree_requirements.csv",
    "prerequisites": "prerequisites.csv",
}

COURSE_HISTORY_KEYS = [
    "the_courses",
    "tpa_courses",
    "tpp_courses",
    "practicum_courses",
]

STUDENT_COLUMNS = [
    "Term",
    "Term Description",
    "Last Name",
    "First Name",
    "UID",
    "Class",
    "Admit Term",
    "Enrolled [Y/N]",
    "Stu Type",
    "Student Type Description",
    "USF Earned Hours",
    "Overall Earned Hours",
    "USF GPA",
    "Theatre Major",
    "Theatre Conc",
]

COURSE_COLUMNS = [
    "Prefix",
    "Number",
    "Course Title",
    "Semester",
    "UID",
    "Name",
    "Grade Mode",
    "Credits",
    "Final Grade Entered",
    "Passing",
    "Passing Override",
]

DEGREE_REQUIREMENT_COLUMNS = [
    "Degree",
    "Conc",
    "Requirement",
    "Course or Credit",
    "Quantity",
    "Courses Accepted",
]

PREREQUISITE_COLUMNS = [
    "Course",
    "Requisite",
    "Min Grade",
    "Concurrency",
    "And/Or",
]

EXPECTED_COLUMNS = {
    "theatre_majors": STUDENT_COLUMNS,
    "the_courses": COURSE_COLUMNS,
    "tpa_courses": COURSE_COLUMNS,
    "tpp_courses": COURSE_COLUMNS,
    "practicum_courses": COURSE_COLUMNS,
    "degree_requirements": DEGREE_REQUIREMENT_COLUMNS,
    "prerequisites": PREREQUISITE_COLUMNS,
}


def get_raw_data_dir():
    # keep the default path relative to the project root.
    return Path(__file__).resolve().parents[1] / "data" / "raw"


def load_csv_file(path):
    # read all csv values as strings so ids and course numbers do not get reshaped.
    return pd.read_csv(Path(path), dtype=str)


def load_all_data(raw_data_dir=None):
    # load every required csv from the raw data folder.
    data_dir = Path(raw_data_dir) if raw_data_dir is not None else get_raw_data_dir()
    data = {}

    for data_key, file_name in REQUIRED_FILES.items():
        file_path = data_dir / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"missing required file: {file_path}")

        data[data_key] = load_csv_file(file_path)

    # validate after loading so callers get a complete column check.
    validate_required_columns(data)
    return data


def validate_required_columns(data):
    # check each loaded table has the columns needed by the first pipeline step.
    missing_messages = []

    for data_key, expected_columns in EXPECTED_COLUMNS.items():
        if data_key not in data:
            missing_messages.append(f"{data_key}: missing dataframe")
            continue

        missing_columns = [
            column for column in expected_columns if column not in data[data_key].columns
        ]
        if missing_columns:
            missing_messages.append(
                f"{data_key}: missing columns {', '.join(missing_columns)}"
            )

    if missing_messages:
        raise ValueError("; ".join(missing_messages))

    return True


def combine_course_history(data):
    # stack the four course history exports into one consistent dataframe.
    validate_required_columns(data)
    course_frames = []

    for data_key in COURSE_HISTORY_KEYS:
        course_frame = data[data_key].copy()
        course_frame["course_code"] = course_frame.apply(
            lambda row: build_course_code(row["Prefix"], row["Number"]),
            axis=1,
        )
        course_frame["source_file"] = data_key
        course_frames.append(course_frame)

    return pd.concat(course_frames, ignore_index=True)
