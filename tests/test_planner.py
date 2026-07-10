# this file tests creation and saving of the student course status dataset.

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.load_data import COURSE_HISTORY_KEYS
from src.planner import (
    build_student_course_status,
    normalize_passing_status,
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
