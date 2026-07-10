# this file tests the course and requirement status planning datasets.

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.load_data import COURSE_HISTORY_KEYS
from src.planner import (
    build_student_course_status,
    build_student_requirement_status,
    evaluate_course_requirement,
    evaluate_credit_requirement,
    get_student_requirements,
    normalize_passing_status,
    parse_accepted_courses,
    save_student_course_status,
)


def make_course_data():
    # create small course exports that cover cleaning and status behavior.
    data = {}

    for index, data_key in enumerate(COURSE_HISTORY_KEYS):
        data[data_key] = pd.DataFrame(
            {
                "UID": [f" u0000000{index + 1} "],
                "Prefix": ["the" if index == 0 else "tpa"],
                "Number": ["2305.0" if index == 0 else str(2200 + index)],
                "Course Title": ["Script Analysis"],
                "Semester": ["Fall 2025"],
                "Credits": ["3"],
                "Grade Mode": ["Standard"],
                "Passing": ["c" if index == 0 else "ip"],
                "Passing Override": [""],
            }
        )

    return data


def test_normalize_passing_status():
    # known source codes should map to readable status values.
    assert normalize_passing_status("c") == "complete"
    assert normalize_passing_status("ip") == "in_progress"
    assert normalize_passing_status("") == "unknown"


def test_build_student_course_status_combines_and_cleans_courses():
    # all course sources should share one clean output schema.
    result = build_student_course_status(make_course_data())

    assert len(result) == 4
    assert {"student_id", "course_code", "status", "source_file"}.issubset(
        result.columns
    )
    assert result.loc[0, "student_id"] == "U00000001"
    assert result.loc[0, "course_code"] == "THE2305"
    assert result.loc[0, "course_number"] == "2305"
    assert result.loc[0, "status"] == "complete"
    assert result["source_file"].nunique() == 4


def test_passing_override_is_used_only_when_passing_is_blank():
    # a useful primary status should take priority over the override field.
    data = make_course_data()
    data["the_courses"].loc[0, ["Passing", "Passing Override"]] = ["", "c"]
    data["tpa_courses"].loc[0, ["Passing", "Passing Override"]] = ["ip", "c"]

    result = build_student_course_status(data)

    assert result.loc[0, "status"] == "complete"
    assert result.loc[1, "status"] == "in_progress"


def test_save_student_course_status_writes_csv(tmp_path):
    # saving should create a csv with the same combined row count.
    output_path = tmp_path / "student_course_status.csv"

    saved_path = save_student_course_status(make_course_data(), output_path)
    saved_data = pd.read_csv(saved_path)

    assert saved_path == output_path
    assert len(saved_data) == 4


def make_requirement_data():
    # create one student with core, concentration, and credit requirements.
    students = pd.DataFrame(
        {
            "UID": [" u00000001 "],
            "Theatre Major": ["TAR"],
            "Theatre Conc": ["TAP"],
        }
    )
    requirements = pd.DataFrame(
        [
            {
                "Degree": "TAR",
                "Conc": "Core",
                "Requirement": "Script Analysis",
                "Course or Credit": "Course",
                "Quantity": "1",
                "Courses Accepted": "THE 2305",
            },
            {
                "Degree": "TAR",
                "Conc": "TAP",
                "Requirement": "Acting II",
                "Course or Credit": "Course",
                "Quantity": "1",
                "Courses Accepted": "TPP3155",
            },
            {
                "Degree": "TAR",
                "Conc": "TAP",
                "Requirement": "Performance Electives",
                "Course or Credit": "Credits",
                "Quantity": "6",
                "Courses Accepted": "TPP 3230, TPP3251C, TPP3252C",
            },
            {
                "Degree": "TAR",
                "Conc": "TDAT",
                "Requirement": "Portfolio",
                "Course or Credit": "Course",
                "Quantity": "1",
                "Courses Accepted": "TPA4993C",
            },
        ]
    )
    courses = pd.DataFrame(
        [
            {
                "student_id": "U00000001",
                "course_code": "THE2305",
                "credits": "3",
                "status": "complete",
            },
            {
                "student_id": "U00000001",
                "course_code": "TPP3155",
                "credits": "3",
                "status": "in_progress",
            },
            {
                "student_id": "U00000001",
                "course_code": "TPP3230",
                "credits": "3",
                "status": "complete",
            },
            {
                "student_id": "U00000001",
                "course_code": "TPP3251C",
                "credits": "3",
                "status": "complete",
            },
        ]
    )
    return students, requirements, courses


def test_parse_accepted_courses_cleans_course_codes():
    # spaces and comma padding should not affect accepted course matching.
    assert parse_accepted_courses("THE 3110, the3111") == ["THE3110", "THE3111"]
    assert parse_accepted_courses("") == []


def test_get_student_requirements_includes_core_and_concentration():
    # students should receive shared core rows and their own concentration rows.
    students, requirements, _ = make_requirement_data()

    result = get_student_requirements(students.iloc[0], requirements)

    assert set(result["Conc"]) == {"Core", "TAP"}
    assert "TDAT" not in set(result["Conc"])


def test_get_student_requirements_supports_mtr_without_concentration():
    # mtr students without a concentration should keep core and mtr degree rows.
    student = pd.Series(
        {"UID": "U00000002", "Theatre Major": "MTR", "Theatre Conc": pd.NA}
    )
    requirements = pd.DataFrame(
        {
            "Degree": ["MTR", "MTR", "TAR"],
            "Conc": ["Core", "MTR", "Core"],
            "Requirement": ["Music Theory", "Voice", "Script Analysis"],
        }
    )

    result = get_student_requirements(student, requirements)

    assert set(result["Requirement"]) == {"Music Theory", "Voice"}


def test_course_requirement_evaluation_matches_cleaned_codes_and_statuses():
    # direct evaluation should clean codes and report each supported course state.
    _, _, courses = make_requirement_data()

    complete = evaluate_course_requirement(courses, ["THE2305"])
    in_progress = evaluate_course_requirement(courses, ["TPP3155"])
    missing = evaluate_course_requirement(courses, ["TPP4180"])

    assert complete["status"] == "complete"
    assert complete["matched_course"] == "THE2305"
    assert in_progress["status"] == "in_progress"
    assert missing["status"] == "missing"


def test_requirement_statuses_match_completed_in_progress_and_missing_courses():
    # course requirements should report the strongest matching course state.
    students, requirements, courses = make_requirement_data()
    missing_requirement = requirements.iloc[[1]].copy()
    missing_requirement["Requirement"] = "Acting III"
    missing_requirement["Courses Accepted"] = "TPP4180"
    requirements = pd.concat([requirements, missing_requirement], ignore_index=True)

    result = build_student_requirement_status(students, requirements, courses)
    statuses = result.set_index("requirement")["status"]

    assert statuses["Script Analysis"] == "complete"
    assert statuses["Acting II"] == "in_progress"
    assert statuses["Acting III"] == "missing"
    matched_courses = result.set_index("requirement")["matched_course"]
    assert matched_courses["Script Analysis"] == "THE2305"


def test_credit_requirement_sums_completed_accepted_credits():
    # enough completed accepted credits should complete a credit requirement.
    students, requirements, courses = make_requirement_data()

    result = build_student_requirement_status(students, requirements, courses)
    credit_result = result[result["requirement"] == "Performance Electives"].iloc[0]

    assert credit_result["status"] == "complete"
    assert credit_result["matched_course"] == "TPP3230,TPP3251C"
    assert credit_result["completed_credits"] == 6
    assert credit_result["in_progress_credits"] == 0


def test_credit_requirement_reports_in_progress_credits():
    # active accepted credits should mark an unfinished credit requirement active.
    _, _, courses = make_requirement_data()

    result = evaluate_credit_requirement(
        courses, ["TPP3230", "TPP3155"], required_quantity=6
    )

    assert result["status"] == "in_progress"
    assert result["completed_credits"] == 3
    assert result["in_progress_credits"] == 3


def test_requirement_output_columns_and_row_count():
    # each applicable core or concentration row should produce one output row.
    students, requirements, courses = make_requirement_data()

    result = build_student_requirement_status(students, requirements, courses)

    assert list(result.columns) == [
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
    assert len(result) == 3
