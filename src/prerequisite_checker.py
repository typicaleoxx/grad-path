# converts intermediate tap data into a long student readiness status csv.

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INTERMEDIATE_PATH = PROJECT_ROOT / "data" / "intermediate" / "tap_intermediate_data.csv"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "intermediate" / "student_readiness_status.csv"

STATUS_MAP = {
    "c": "complete",
    "ip": "in_progress",
    "r": "missing_ready",
    "n": "missing_blocked",
}

PREREQ_READY_MAP = {
    "c": "yes",
    "ip": "yes",
    "r": "yes",
    "n": "no",
}

READINESS_REASON_MAP = {
    "c": "requirement is already complete",
    "ip": "requirement is currently in progress",
    "r": "requirement is missing but student appears ready based on intermediate data",
    "n": "requirement is missing and student appears blocked based on intermediate data",
}

OUTPUT_COLUMNS = [
    "student_id",
    "student_name",
    "term",
    "class_year",
    "admit_term",
    "student_type",
    "usf_earned_hours",
    "overall_earned_hours",
    "gpa",
    "degree",
    "concentration",
    "requirement",
    "status_code",
    "need_status",
    "distance",
    "semester_bucket",
    "prereq_ready",
    "missing_prerequisites",
    "readiness_reason",
]


def load_intermediate_data(path=None):
    path = Path(path) if path else DEFAULT_INTERMEDIATE_PATH
    return pd.read_csv(path)


def get_student_columns():
    return {
        "Term",
        "Last Name",
        "First Name",
        "UID",
        "Class",
        "Admit Term",
        "Stu Type",
        "USF Earned Hours",
        "Overall Earned Hours",
        "USF GPA",
        "Theatre Major",
        "Theatre Conc",
    }


def is_requirement_column(column_name, student_columns):
    if column_name in student_columns:
        return False
    if str(column_name).endswith(" Dist"):
        return False
    if str(column_name).startswith("Unnamed:"):
        return False
    return True


def normalize_status(value):
    if pd.isna(value):
        return ""
    return STATUS_MAP.get(str(value).strip().lower(), "")


def get_semester_bucket(distance_value):
    if pd.isna(distance_value):
        return ""

    distance = str(distance_value).strip()
    if not distance or distance == "0":
        return ""
    # if distance == "9":
    #     return "needed_4_plus_semesters"
    if "/" in distance:
        first_value = distance.split("/", 1)[0]
        if first_value.isdigit():
            semesters = int(first_value)
            if semesters == 1:
                return "needed_1_semester"
            if semesters == 2:
                return "needed_2_semesters"
            if semesters == 3:
                return "needed_3_semesters"
            if semesters >= 4:
                return "needed_4_plus_semesters"
    return ""


def build_student_readiness_status(intermediate_df):
    student_columns = get_student_columns()
    requirement_columns = [
        column
        for column in intermediate_df.columns
        if is_requirement_column(column, student_columns)
        and _column_has_status_values(intermediate_df[column])
    ]

    rows = []
    for _, student in intermediate_df.iterrows():
        for requirement in requirement_columns:
            status_code = _clean_value(student.get(requirement)).lower()
            distance = _clean_value(student.get(f"{requirement} Dist", ""))

            rows.append(
                {
                    "student_id": _clean_value(student.get("UID")),
                    "student_name": _student_name(student),
                    "term": student.get("Term", ""),
                    "class_year": student.get("Class", ""),
                    "admit_term": student.get("Admit Term", ""),
                    "student_type": _clean_value(student.get("Stu Type")),
                    "usf_earned_hours": student.get("USF Earned Hours", ""),
                    "overall_earned_hours": student.get("Overall Earned Hours", ""),
                    "gpa": student.get("USF GPA", ""),
                    "degree": _clean_value(student.get("Theatre Major")),
                    "concentration": _clean_value(student.get("Theatre Conc")),
                    "requirement": requirement,
                    "status_code": status_code,
                    "need_status": normalize_status(status_code),
                    "distance": distance,
                    "semester_bucket": get_semester_bucket(distance),
                    "prereq_ready": PREREQ_READY_MAP.get(status_code, ""),
                    "missing_prerequisites": _missing_prerequisites(status_code),
                    "readiness_reason": READINESS_REASON_MAP.get(status_code, ""),
                }
            )

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def save_student_readiness_status(intermediate_path=None, output_path=None):
    output_path = Path(output_path) if output_path else DEFAULT_OUTPUT_PATH
    intermediate_df = load_intermediate_data(intermediate_path)
    readiness_df = build_student_readiness_status(intermediate_df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    readiness_df.to_csv(output_path, index=False)
    return output_path, len(readiness_df)


# keep requirement detection tied to the actual status values in the file.
def _column_has_status_values(series):
    values = series.dropna().astype(str).str.strip().str.lower()
    return values.isin(STATUS_MAP).any() and values.isin(STATUS_MAP).all()


# keep csv strings clean without turning blanks into nan text.
def _clean_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def _student_name(student):
    first_name = _clean_value(student.get("First Name"))
    last_name = _clean_value(student.get("Last Name"))
    return " ".join(part for part in [first_name, last_name] if part)


def _missing_prerequisites(status_code):
    if status_code == "n":
        return "unknown prerequisite or earlier requirement"
    return ""


if __name__ == "__main__":
    saved_path, row_count = save_student_readiness_status()
    print(saved_path)
    print(f"rows written: {row_count}")
