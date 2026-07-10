# this file creates initial demand and priority reports from readiness data.

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
READINESS_STATUS_PATH = (
    PROJECT_ROOT / "data" / "intermediate" / "student_readiness_status.csv"
)
COURSE_DEMAND_PATH = PROJECT_ROOT / "outputs" / "course_demand_report.csv"
PRIORITY_STUDENTS_PATH = PROJECT_ROOT / "outputs" / "priority_students.csv"

DEMAND_COLUMNS = [
    "course_code",
    "needed_1_semester",
    "needed_2_semesters",
    "needed_3_semesters",
    "needed_4_plus_semesters",
    "total_demand",
]

PRIORITY_COLUMNS = ["student_id", "course_code", "priority", "reason"]


def load_readiness_status(path=READINESS_STATUS_PATH):
    # read readiness values as strings before assigning report categories.
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


def save_reports(
    readiness_status,
    demand_path=COURSE_DEMAND_PATH,
    priority_path=PRIORITY_STUDENTS_PATH,
):
    # create the output folder and save both initial final reports.
    demand_destination = Path(demand_path)
    priority_destination = Path(priority_path)
    demand_destination.parent.mkdir(parents=True, exist_ok=True)
    priority_destination.parent.mkdir(parents=True, exist_ok=True)

    demand_report = build_course_demand_report(readiness_status)
    priority_report = build_priority_students_report(readiness_status)
    demand_report.to_csv(demand_destination, index=False)
    priority_report.to_csv(priority_destination, index=False)
    return demand_destination, demand_report, priority_destination, priority_report


if __name__ == "__main__":
    # generate both reports from the prerequisite readiness output.
    readiness_data = load_readiness_status()
    demand_path, demand_data, priority_path, priority_data = save_reports(
        readiness_data
    )
    print(f"saved {len(demand_data)} rows to {demand_path}")
    print(f"saved {len(priority_data)} rows to {priority_path}")
