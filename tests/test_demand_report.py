# this file tests initial demand aggregation and student priority reporting.

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.demand_report import (
    DEMAND_COLUMNS,
    GRADUATION_COLUMNS,
    PRIORITY_COLUMNS,
    build_course_demand_report,
    build_priority_students_report,
    build_student_graduation_summary,
)


def make_readiness_status():
    # include one ready and one blocked student need for report tests.
    return pd.DataFrame(
        {
            "student_id": ["U00000001", "U00000002"],
            "course_code": ["THE4000", "THE4000"],
            "prereq_ready": ["yes", "no"],
            "readiness_reason": [
                "all prerequisites are complete or in progress",
                "one or more prerequisites are missing",
            ],
        }
    )


def make_requirement_status():
    # create students with close and needs-planning graduation states.
    rows = []
    for status in ["complete", "complete", "in_progress", "missing", "missing"]:
        rows.append(
            {
                "student_id": "U00000001",
                "degree": "TAR",
                "concentration": "TAP",
                "requirement": f"Student One {len(rows) + 1}",
                "status": status,
            }
        )

    for index in range(7):
        rows.append(
            {
                "student_id": "U00000002",
                "degree": "TAR",
                "concentration": "TDAT",
                "requirement": f"Student Two {index + 1}",
                "status": "missing",
            }
        )
    return pd.DataFrame(rows)


def test_ready_and_blocked_courses_use_expected_need_categories():
    # readiness should split demand into one-semester and two-semester counts.
    report = build_course_demand_report(make_readiness_status())

    assert report.loc[0, "needed_1_semester"] == 1
    assert report.loc[0, "needed_2_semesters"] == 1
    assert report.loc[0, "total_demand"] == 2


def test_priority_matches_prerequisite_readiness():
    # ready students receive high priority while blocked students receive none.
    report = build_priority_students_report(make_readiness_status())

    priorities = report.set_index("student_id")["priority"]
    assert priorities["U00000001"] == "high"
    assert priorities["U00000002"] == "none"


def test_output_report_columns_exist():
    # both final reports should use the agreed output schemas.
    readiness = make_readiness_status()

    assert list(build_course_demand_report(readiness).columns) == DEMAND_COLUMNS
    assert list(build_priority_students_report(readiness).columns) == PRIORITY_COLUMNS


def test_student_graduation_summary_columns_and_completion_percent():
    # summary output should use the agreed schema and rounded completion math.
    summary = build_student_graduation_summary(
        make_requirement_status(), make_readiness_status()
    )
    student = summary.set_index("student_id").loc["U00000001"]

    assert list(summary.columns) == GRADUATION_COLUMNS
    assert student["completion_percent"] == 40.0


def test_graduation_status_uses_missing_requirement_count():
    # two missing rows are close while more than five need additional planning.
    summary = build_student_graduation_summary(
        make_requirement_status(), make_readiness_status()
    ).set_index("student_id")

    assert summary.loc["U00000001", "graduation_status"] == "close"
    assert summary.loc["U00000002", "graduation_status"] == "needs planning"
