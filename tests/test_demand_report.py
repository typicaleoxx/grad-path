# this file tests initial demand aggregation and student priority reporting.

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.demand_report import (
    DEMAND_COLUMNS,
    PRIORITY_COLUMNS,
    build_course_demand_report,
    build_priority_students_report,
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
