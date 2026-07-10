# tests student graduation summary, course demand, and priority student reports.

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.demand_report import (
    assign_priority,
    build_course_demand_report,
    build_priority_students_report,
    build_student_graduation_summary,
    get_graduation_status,
)


SUMMARY_COLUMNS = [
    "student_id",
    "student_name",
    "degree",
    "concentration",
    "class_year",
    "usf_earned_hours",
    "overall_earned_hours",
    "gpa",
    "total_requirements",
    "complete_requirements",
    "in_progress_requirements",
    "ready_missing_requirements",
    "blocked_missing_requirements",
    "missing_requirements",
    "completion_percent",
    "graduation_status",
]

DEMAND_COLUMNS = [
    "requirement",
    "needed_1_semester",
    "needed_2_semesters",
    "needed_3_semesters",
    "needed_4_plus_semesters",
    "ready_students",
    "blocked_students",
    "total_demand",
]

PRIORITY_COLUMNS = [
    "student_id",
    "student_name",
    "degree",
    "concentration",
    "class_year",
    "requirement",
    "need_status",
    "distance",
    "semester_bucket",
    "priority",
    "reason",
]


def test_get_graduation_status_maps_missing_counts():
    assert get_graduation_status(0) == "ready or nearly complete"
    assert get_graduation_status(2) == "close"
    assert get_graduation_status(5) == "moderate remaining"
    assert get_graduation_status(6) == "needs planning"


def test_build_student_graduation_summary_creates_one_row_per_student():
    readiness_df = pd.DataFrame(
        [
            _readiness_row("U1", "Student One", "complete"),
            _readiness_row("U1", "Student One", "in_progress"),
            _readiness_row("U1", "Student One", "missing_ready"),
            _readiness_row("U1", "Student One", "missing_blocked"),
            _readiness_row("U2", "Student Two", "complete", class_year=2),
            _readiness_row("U2", "Student Two", "complete", class_year=2),
        ]
    )

    result = build_student_graduation_summary(readiness_df)

    assert len(result) == 2
    assert list(result.columns) == SUMMARY_COLUMNS


def test_build_student_graduation_summary_calculates_totals():
    readiness_df = pd.DataFrame(
        [
            _readiness_row("U1", "Student One", "complete"),
            _readiness_row("U1", "Student One", "complete"),
            _readiness_row("U1", "Student One", "in_progress"),
            _readiness_row("U1", "Student One", "missing_ready"),
            _readiness_row("U1", "Student One", "missing_blocked"),
        ]
    )

    result = build_student_graduation_summary(readiness_df)
    row = result.iloc[0]

    assert row["total_requirements"] == 5
    assert row["complete_requirements"] == 2
    assert row["in_progress_requirements"] == 1
    assert row["ready_missing_requirements"] == 1
    assert row["blocked_missing_requirements"] == 1
    assert row["missing_requirements"] == 2
    assert row["completion_percent"] == 40.0
    assert row["graduation_status"] == "close"


def test_build_course_demand_report_counts_missing_demand_only():
    readiness_df = pd.DataFrame(
        [
            _demand_row("Acting II", "missing_ready", "needed_1_semester"),
            _demand_row("Acting II", "missing_blocked", "needed_2_semesters"),
            _demand_row("Acting II", "complete", "needed_1_semester"),
            _demand_row("Acting II", "in_progress", "needed_2_semesters"),
            _demand_row("Script Analysis", "missing_ready", "needed_1_semester"),
        ]
    )

    result = build_course_demand_report(readiness_df)
    acting_row = result[result["requirement"] == "Acting II"].iloc[0]

    assert list(result.columns) == DEMAND_COLUMNS
    assert acting_row["needed_1_semester"] == 1
    assert acting_row["needed_2_semesters"] == 1
    assert acting_row["ready_students"] == 1
    assert acting_row["blocked_students"] == 1
    assert acting_row["total_demand"] == 2


def test_build_course_demand_report_sorts_by_total_demand_descending():
    readiness_df = pd.DataFrame(
        [
            _demand_row("Lower Demand", "missing_ready", "needed_1_semester"),
            _demand_row("Higher Demand", "missing_ready", "needed_1_semester"),
            _demand_row("Higher Demand", "missing_blocked", "needed_3_semesters"),
            _demand_row("Another Higher Demand", "missing_ready", "needed_4_plus_semesters"),
            _demand_row("Another Higher Demand", "missing_blocked", "needed_4_plus_semesters"),
        ]
    )

    result = build_course_demand_report(readiness_df)

    assert result["requirement"].tolist() == [
        "Another Higher Demand",
        "Higher Demand",
        "Lower Demand",
    ]


def test_assign_priority_maps_ready_and_blocked_rows():
    assert assign_priority("missing_ready", "needed_1_semester") == "high"
    assert assign_priority("missing_ready", "needed_2_semesters") == "medium"
    assert assign_priority("missing_ready", "needed_3_semesters") == "low"
    assert assign_priority("missing_ready", "needed_4_plus_semesters") == "low"
    assert assign_priority("missing_blocked", "needed_1_semester") == "none"


def test_build_priority_students_report_keeps_missing_rows_only():
    readiness_df = pd.DataFrame(
        [
            _priority_row("U1", "complete", "needed_1_semester"),
            _priority_row("U1", "in_progress", "needed_2_semesters"),
            _priority_row("U1", "missing_ready", "needed_1_semester"),
            _priority_row("U2", "missing_blocked", "needed_1_semester"),
        ]
    )

    result = build_priority_students_report(readiness_df)

    assert list(result.columns) == PRIORITY_COLUMNS
    assert len(result) == 2
    assert result["need_status"].tolist() == ["missing_ready", "missing_blocked"]


def test_build_priority_students_report_sorts_by_priority_order():
    readiness_df = pd.DataFrame(
        [
            _priority_row("U4", "missing_blocked", "needed_1_semester", "Blocked"),
            _priority_row("U3", "missing_ready", "needed_3_semesters", "Low"),
            _priority_row("U1", "missing_ready", "needed_1_semester", "High"),
            _priority_row("U2", "missing_ready", "needed_2_semesters", "Medium"),
        ]
    )

    result = build_priority_students_report(readiness_df)

    assert result["priority"].tolist() == ["high", "medium", "low", "none"]


# keep fixture rows tiny so the summary math is the thing under test.
def _readiness_row(student_id, student_name, need_status, class_year=1):
    return {
        "student_id": student_id,
        "student_name": student_name,
        "degree": "TAR",
        "concentration": "TAP",
        "class_year": class_year,
        "usf_earned_hours": 30,
        "overall_earned_hours": 45,
        "gpa": 3.4,
        "requirement": "Some Requirement",
        "need_status": need_status,
    }


def _demand_row(requirement, need_status, semester_bucket):
    return {
        "student_id": "U1",
        "student_name": "Student One",
        "degree": "TAR",
        "concentration": "TAP",
        "requirement": requirement,
        "status_code": "r",
        "need_status": need_status,
        "distance": "1/4",
        "semester_bucket": semester_bucket,
        "prereq_ready": "yes",
    }


def _priority_row(student_id, need_status, semester_bucket, requirement="Acting II"):
    return {
        "student_id": student_id,
        "student_name": f"Student {student_id}",
        "degree": "TAR",
        "concentration": "TAP",
        "class_year": 2,
        "requirement": requirement,
        "need_status": need_status,
        "distance": "1/4",
        "semester_bucket": semester_bucket,
    }
