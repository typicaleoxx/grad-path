# this file builds course and requirement status datasets for the planning pipeline.

from pathlib import Path

import pandas as pd

# support package imports and direct execution from the project root.
try:
    from src.load_data import (
        COURSE_HISTORY_KEYS,
        REQUIRED_FILES,
        load_all_data,
    )
    from src.utils import (
        build_course_code,
        clean_course_number,
        clean_student_id,
        normalize_text,
    )
except ModuleNotFoundError:
    from load_data import (
        COURSE_HISTORY_KEYS,
        REQUIRED_FILES,
        load_all_data,
    )
    from utils import (
        build_course_code,
        clean_course_number,
        clean_student_id,
        normalize_text,
    )


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

REQUIREMENT_OUTPUT_COLUMNS = [
    "student_id",
    "degree",
    "concentration",
    "requirement",
    "course_or_credit",
    "quantity",
    "accepted_courses",
    "status",
    "matched_course",
    "completed_credits",
    "in_progress_credits",
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


def parse_accepted_courses(value):
    # split requirement options and remove spacing differences from course codes.
    if pd.isna(value):
        return []

    accepted_courses = []
    for course_code in str(value).split(","):
        clean_code = "".join(course_code.strip().upper().split())
        if clean_code:
            accepted_courses.append(clean_code)

    return accepted_courses


def get_student_requirements(student_row, degree_requirements):
    # include shared core rows and rows for the student's concentration.
    degree = normalize_text(student_row.get("Theatre Major", ""))
    concentration = normalize_text(student_row.get("Theatre Conc", ""))
    requirement_degrees = degree_requirements["Degree"].map(normalize_text)
    requirement_concentrations = degree_requirements["Conc"].map(normalize_text)
    concentration_matches = requirement_concentrations.eq("core")

    if concentration:
        concentration_matches |= requirement_concentrations.eq(concentration)
    else:
        concentration_matches |= requirement_concentrations.isin(["", degree])

    return degree_requirements[
        requirement_degrees.eq(degree) & concentration_matches
    ].copy()


def _matched_course_records(student_courses, accepted_courses):
    # normalize course codes once more so externally supplied dataframes also match.
    accepted_set = set(accepted_courses)
    clean_codes = student_courses["course_code"].map(
        lambda value: "".join(str(value).strip().upper().split())
        if not pd.isna(value)
        else ""
    )
    return student_courses[clean_codes.isin(accepted_set)].assign(course_code=clean_codes)


def _credit_totals(matched_courses):
    # calculate numeric credit totals for completed and active accepted courses.
    completed = matched_courses[matched_courses["status"] == "complete"]
    in_progress = matched_courses[matched_courses["status"] == "in_progress"]
    completed_credits = pd.to_numeric(
        completed["credits"], errors="coerce"
    ).fillna(0).sum()
    in_progress_credits = pd.to_numeric(
        in_progress["credits"], errors="coerce"
    ).fillna(0).sum()
    return completed, in_progress, completed_credits, in_progress_credits


def evaluate_course_requirement(student_courses, accepted_courses):
    # completed work takes priority over an in-progress accepted course.
    matched_courses = _matched_course_records(student_courses, accepted_courses)
    completed, in_progress, completed_credits, in_progress_credits = (
        _credit_totals(matched_courses)
    )

    if not completed.empty:
        status = "complete"
        matched_course = completed.iloc[0]["course_code"]
    elif not in_progress.empty:
        status = "in_progress"
        matched_course = in_progress.iloc[0]["course_code"]
    else:
        status = "missing"
        matched_course = ""

    return {
        "status": status,
        "matched_course": matched_course,
        "completed_credits": completed_credits,
        "in_progress_credits": in_progress_credits,
    }


def evaluate_credit_requirement(
    student_courses, accepted_courses, required_quantity
):
    # sum completed accepted credits and note accepted work still in progress.
    matched_courses = _matched_course_records(student_courses, accepted_courses)
    completed, in_progress, completed_credits, in_progress_credits = (
        _credit_totals(matched_courses)
    )
    required_credits = pd.to_numeric(
        pd.Series([required_quantity]), errors="coerce"
    ).fillna(0).iloc[0]

    if completed_credits >= required_credits:
        status = "complete"
        matched = completed
    elif in_progress_credits > 0:
        status = "in_progress"
        matched = pd.concat([completed, in_progress], ignore_index=True)
    else:
        status = "missing"
        matched = completed

    matched_codes = ",".join(dict.fromkeys(matched["course_code"].tolist()))
    return {
        "status": status,
        "matched_course": matched_codes,
        "completed_credits": completed_credits,
        "in_progress_credits": in_progress_credits,
    }


def build_student_requirement_status(students_df, requirements_df, course_status_df):
    # compare each unique student with core and concentration requirements.
    rows = []
    students = students_df.drop_duplicates(subset=["UID"], keep="last")

    for _, student in students.iterrows():
        student_id = clean_student_id(student["UID"])
        student_requirements = get_student_requirements(student, requirements_df)
        student_courses = course_status_df[
            course_status_df["student_id"].map(clean_student_id).eq(student_id)
        ]

        for _, requirement_row in student_requirements.iterrows():
            accepted_courses = parse_accepted_courses(
                requirement_row["Courses Accepted"]
            )
            requirement_type = normalize_text(requirement_row["Course or Credit"])

            if requirement_type == "credits":
                result = evaluate_credit_requirement(
                    student_courses,
                    accepted_courses,
                    requirement_row["Quantity"],
                )
            else:
                result = evaluate_course_requirement(
                    student_courses, accepted_courses
                )

            rows.append(
                {
                    "student_id": student_id,
                    "degree": str(student["Theatre Major"]).strip(),
                    "concentration": (
                        "" if pd.isna(student["Theatre Conc"])
                        else str(student["Theatre Conc"]).strip()
                    ),
                    "requirement": requirement_row["Requirement"],
                    "course_or_credit": requirement_row["Course or Credit"],
                    "quantity": requirement_row["Quantity"],
                    "accepted_courses": ",".join(accepted_courses),
                    "status": result["status"],
                    "matched_course": result["matched_course"],
                    "completed_credits": result["completed_credits"],
                    "in_progress_credits": result["in_progress_credits"],
                }
            )

    return pd.DataFrame(rows, columns=REQUIREMENT_OUTPUT_COLUMNS)


def save_student_requirement_status(
    students_df,
    requirements_df,
    course_status_df,
    output_path=None,
):
    # save requirement matching results in the intermediate data folder.
    default_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "intermediate"
        / "student_requirement_status.csv"
    )
    destination = Path(output_path) if output_path is not None else default_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    requirement_status = build_student_requirement_status(
        students_df, requirements_df, course_status_df
    )
    requirement_status.to_csv(destination, index=False)
    return destination


if __name__ == "__main__":
    # rebuild both intermediate planning datasets from the project inputs.
    loaded_data = load_all_data()
    course_path = save_student_course_status(loaded_data)
    course_status = pd.read_csv(course_path, dtype=str)
    requirement_path = save_student_requirement_status(
        loaded_data["theatre_majors"],
        loaded_data["degree_requirements"],
        course_status,
    )
    requirement_status = pd.read_csv(requirement_path, dtype=str)

    print(f"saved {len(course_status)} rows to {course_path}")
    print(f"saved {len(requirement_status)} rows to {requirement_path}")
