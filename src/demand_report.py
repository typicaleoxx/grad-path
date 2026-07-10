# this file creates demand, priority, and graduation progress reports.

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
READINESS_STATUS_PATH = (
    PROJECT_ROOT / "data" / "intermediate" / "student_readiness_status.csv"
)
REQUIREMENT_STATUS_PATH = (
    PROJECT_ROOT / "data" / "intermediate" / "student_requirement_status.csv"
)
COURSE_DEMAND_PATH = PROJECT_ROOT / "outputs" / "course_demand_report.csv"
PRIORITY_STUDENTS_PATH = PROJECT_ROOT / "outputs" / "priority_students.csv"
GRADUATION_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "student_graduation_summary.csv"

DEMAND_COLUMNS = [
    "course_code",
    "needed_1_semester",
    "needed_2_semesters",
    "needed_3_semesters",
    "needed_4_plus_semesters",
    "total_demand",
]

PRIORITY_COLUMNS = ["student_id", "course_code", "priority", "reason"]

GRADUATION_COLUMNS = [
    "student_id",
    "degree",
    "concentration",
    "total_requirements",
    "complete_requirements",
    "in_progress_requirements",
    "missing_requirements",
    "ready_missing_requirements",
    "blocked_missing_requirements",
    "completion_percent",
    "graduation_status",
]


def load_readiness_status(path=READINESS_STATUS_PATH):
    # read readiness values as strings before assigning report categories.
    return pd.read_csv(Path(path), dtype=str).fillna("")


def load_requirement_status(path=REQUIREMENT_STATUS_PATH):
    # read requirement rows used to calculate each student's progress.
    return pd.read_csv(Path(path), dtype=str).fillna("")


def add_planning_categories(readiness_status):
    # map readiness directly to the first prototype need and priority rules.
    planned = readiness_status.copy()
    ready = planned["prereq_ready"].str.lower().eq("yes")
    planned["need_category"] = ready.map(
        {True: "needed_1_semester", False: "needed_2_semesters"}
    )
    planned["priority"] = ready.map({True: "high", False: "none"})
    planned["priority_reason"] = ready.map(
        {
            True: "prerequisites are complete or not required",
            False: "one or more prerequisites are missing",
        }
    )
    return planned


def build_course_demand_report(readiness_status):
    # count each course by need category and keep future columns visible.
    planned = add_planning_categories(readiness_status)
    counts = (
        planned.groupby(["course_code", "need_category"])
        .size()
        .unstack(fill_value=0)
    )

    for column in DEMAND_COLUMNS[1:-1]:
        if column not in counts.columns:
            counts[column] = 0

    counts = counts[DEMAND_COLUMNS[1:-1]]
    counts["total_demand"] = counts.sum(axis=1)
    return counts.reset_index()[DEMAND_COLUMNS]


def build_priority_students_report(readiness_status):
    # keep every student need so high and none priorities remain reviewable.
    planned = add_planning_categories(readiness_status)
    report = planned.rename(columns={"priority_reason": "reason"})
    return report[PRIORITY_COLUMNS]


def get_graduation_status(missing_requirements):
    # translate the remaining requirement count into a readable planning label.
    if missing_requirements == 0:
        return "ready or nearly complete"
    if missing_requirements <= 2:
        return "close"
    if missing_requirements <= 5:
        return "moderate remaining"
    return "needs planning"


def build_student_graduation_summary(requirement_status, readiness_status):
    # count requirement states for each student before joining readiness totals.
    requirements = requirement_status.copy()
    requirements["status"] = requirements["status"].str.lower()
    student_details = requirements.groupby("student_id", as_index=False).agg(
        degree=("degree", "first"),
        concentration=("concentration", "first"),
        total_requirements=("requirement", "size"),
    )

    status_counts = (
        requirements.groupby(["student_id", "status"])
        .size()
        .unstack(fill_value=0)
    )
    for status in ["complete", "in_progress", "missing"]:
        if status not in status_counts.columns:
            status_counts[status] = 0

    status_counts = status_counts[
        ["complete", "in_progress", "missing"]
    ].rename(
        columns={
            "complete": "complete_requirements",
            "in_progress": "in_progress_requirements",
            "missing": "missing_requirements",
        }
    )

    # count ready and blocked missing courses from prerequisite checking.
    readiness = readiness_status.copy()
    readiness["prereq_ready"] = readiness["prereq_ready"].str.lower()
    readiness_counts = (
        readiness.groupby(["student_id", "prereq_ready"])
        .size()
        .unstack(fill_value=0)
    )
    for ready_value in ["yes", "no"]:
        if ready_value not in readiness_counts.columns:
            readiness_counts[ready_value] = 0

    readiness_counts = readiness_counts[["yes", "no"]].rename(
        columns={
            "yes": "ready_missing_requirements",
            "no": "blocked_missing_requirements",
        }
    )

    # combine the counts and calculate the final student-level fields.
    summary = student_details.merge(
        status_counts.reset_index(), on="student_id", how="left"
    ).merge(readiness_counts.reset_index(), on="student_id", how="left")
    count_columns = GRADUATION_COLUMNS[3:9]
    summary[count_columns] = summary[count_columns].fillna(0).astype(int)
    summary["completion_percent"] = (
        summary["complete_requirements"] / summary["total_requirements"] * 100
    ).round(2)
    summary["graduation_status"] = summary["missing_requirements"].map(
        get_graduation_status
    )
    return summary[GRADUATION_COLUMNS]


def save_reports(
    readiness_status,
    requirement_status=None,
    demand_path=COURSE_DEMAND_PATH,
    priority_path=PRIORITY_STUDENTS_PATH,
    graduation_path=GRADUATION_SUMMARY_PATH,
):
    # create the output folder and save all final analytics reports.
    if requirement_status is None:
        requirement_status = load_requirement_status()

    demand_destination = Path(demand_path)
    priority_destination = Path(priority_path)
    graduation_destination = Path(graduation_path)
    demand_destination.parent.mkdir(parents=True, exist_ok=True)
    priority_destination.parent.mkdir(parents=True, exist_ok=True)
    graduation_destination.parent.mkdir(parents=True, exist_ok=True)

    demand_report = build_course_demand_report(readiness_status)
    priority_report = build_priority_students_report(readiness_status)
    graduation_summary = build_student_graduation_summary(
        requirement_status, readiness_status
    )
    demand_report.to_csv(demand_destination, index=False)
    priority_report.to_csv(priority_destination, index=False)
    graduation_summary.to_csv(graduation_destination, index=False)
    return (
        demand_destination,
        demand_report,
        priority_destination,
        priority_report,
        graduation_destination,
        graduation_summary,
    )


if __name__ == "__main__":
    # generate all reports from requirement and prerequisite readiness data.
    readiness_data = load_readiness_status()
    requirement_data = load_requirement_status()
    (
        demand_path,
        demand_data,
        priority_path,
        priority_data,
        graduation_path,
        graduation_data,
    ) = save_reports(
        readiness_data,
        requirement_data,
    )
    print(f"saved {len(demand_data)} rows to {demand_path}")
    print(f"saved {len(priority_data)} rows to {priority_path}")
    print(f"saved {len(graduation_data)} rows to {graduation_path}")
