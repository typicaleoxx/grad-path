# this file checks prerequisite readiness for missing student requirements.

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENT_STATUS_PATH = (
    PROJECT_ROOT / "data" / "intermediate" / "student_requirement_status.csv"
)
PREREQUISITES_PATH = PROJECT_ROOT / "data" / "raw" / "prerequisites.csv"
READINESS_STATUS_PATH = (
    PROJECT_ROOT / "data" / "intermediate" / "student_readiness_status.csv"
)

READINESS_COLUMNS = [
    "student_id",
    "degree",
    "concentration",
    "requirement",
    "course_code",
    "need_status",
    "prereq_ready",
    "missing_prerequisites",
    "readiness_reason",
]


def clean_course_code(value):
    # remove case and spacing differences before comparing course codes.
    if pd.isna(value):
        return ""
    return "".join(str(value).strip().upper().split())


def parse_course_codes(value):
    # split comma-separated course fields into clean individual codes.
    if pd.isna(value):
        return []
    return [
        code
        for code in (clean_course_code(item) for item in str(value).split(","))
        if code
    ]


def load_requirement_status(path=REQUIREMENT_STATUS_PATH):
    # read the intermediate requirement records as stable string values.
    return pd.read_csv(Path(path), dtype=str).fillna("")


def load_prerequisites(path=PREREQUISITES_PATH):
    # read the simple prerequisite rules used by this prototype step.
    return pd.read_csv(Path(path), dtype=str).fillna("")


def get_available_courses(student_rows):
    # completed and in-progress matched courses both satisfy prototype readiness.
    available = set()
    active_rows = student_rows[
        student_rows["status"].str.lower().isin(["complete", "in_progress"])
    ]
    for value in active_rows["matched_course"]:
        available.update(parse_course_codes(value))
    return available


def check_course_readiness(course_code, available_courses, prerequisites):
    # treat every listed requisite as required in this simplified first version.
    clean_target = clean_course_code(course_code)
    rule_courses = prerequisites["Course"].map(clean_course_code)
    course_rules = prerequisites[rule_courses.eq(clean_target)]
    required_courses = [
        clean_course_code(value) for value in course_rules["Requisite"] if value
    ]

    if not required_courses:
        return "yes", "", "no prerequisites listed"

    missing = [code for code in required_courses if code not in available_courses]
    if not missing:
        return "yes", "", "all prerequisites are complete or in progress"

    return "no", ",".join(missing), "one or more prerequisites are missing"


def build_student_readiness_status(requirement_status, prerequisites):
    # create one readiness row for each course attached to a missing requirement.
    rows = []
    missing_rows = requirement_status[
        requirement_status["status"].str.lower().eq("missing")
    ]

    for _, requirement_row in missing_rows.iterrows():
        student_rows = requirement_status[
            requirement_status["student_id"].eq(requirement_row["student_id"])
        ]
        available_courses = get_available_courses(student_rows)

        for course_code in parse_course_codes(requirement_row["accepted_courses"]):
            ready, missing_prerequisites, reason = check_course_readiness(
                course_code, available_courses, prerequisites
            )
            rows.append(
                {
                    "student_id": requirement_row["student_id"],
                    "degree": requirement_row["degree"],
                    "concentration": requirement_row["concentration"],
                    "requirement": requirement_row["requirement"],
                    "course_code": course_code,
                    "need_status": "missing",
                    "prereq_ready": ready,
                    "missing_prerequisites": missing_prerequisites,
                    "readiness_reason": reason,
                }
            )

    return pd.DataFrame(rows, columns=READINESS_COLUMNS)


def save_student_readiness_status(
    requirement_status,
    prerequisites,
    output_path=READINESS_STATUS_PATH,
):
    # write the readiness dataset to the intermediate folder.
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    readiness = build_student_readiness_status(requirement_status, prerequisites)
    readiness.to_csv(destination, index=False)
    return destination, readiness


if __name__ == "__main__":
    # run prerequisite checking from the mock intermediate requirement data.
    requirement_data = load_requirement_status()
    prerequisite_data = load_prerequisites()
    saved_path, readiness_data = save_student_readiness_status(
        requirement_data, prerequisite_data
    )
    print(f"saved {len(readiness_data)} rows to {saved_path}")
