# this file tests prerequisite readiness for missing student requirements.

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.prerequisite_checker import (
    READINESS_COLUMNS,
    build_student_readiness_status,
)


def make_requirement_status(prerequisite_status=None):
    # build one missing target and an optional prerequisite course record.
    rows = [
        {
            "student_id": "U00000001",
            "degree": "TAR",
            "concentration": "TAP",
            "requirement": "Advanced Course",
            "accepted_courses": "THE4000",
            "status": "missing",
            "matched_course": "",
        }
    ]
    if prerequisite_status is not None:
        rows.append(
            {
                "student_id": "U00000001",
                "degree": "TAR",
                "concentration": "TAP",
                "requirement": "Foundation Course",
                "accepted_courses": "THE3000",
                "status": prerequisite_status,
                "matched_course": "THE3000",
            }
        )
    return pd.DataFrame(rows)


def make_prerequisites(include_rule=True):
    # create a simple single-course prerequisite rule when requested.
    if not include_rule:
        return pd.DataFrame(columns=["Course", "Requisite", "Min Grade", "Concurrency", "And/Or"])
    return pd.DataFrame(
        {
            "Course": ["THE4000"],
            "Requisite": ["THE3000"],
            "Min Grade": ["C"],
            "Concurrency": ["No"],
            "And/Or": [""],
        }
    )


def test_missing_course_without_prerequisites_is_ready():
    # courses without listed rules can move directly into near-term demand.
    result = build_student_readiness_status(
        make_requirement_status(), make_prerequisites(include_rule=False)
    )

    assert result.loc[0, "prereq_ready"] == "yes"


def test_completed_prerequisite_is_ready():
    # completed prerequisite work should satisfy the prototype check.
    result = build_student_readiness_status(
        make_requirement_status("complete"), make_prerequisites()
    )

    assert result.loc[0, "prereq_ready"] == "yes"


def test_in_progress_prerequisite_is_ready():
    # active prerequisite work also counts as ready in the first version.
    result = build_student_readiness_status(
        make_requirement_status("in_progress"), make_prerequisites()
    )

    assert result.loc[0, "prereq_ready"] == "yes"


def test_missing_prerequisite_is_not_ready():
    # an unavailable prerequisite should remain visible in the output reason.
    result = build_student_readiness_status(
        make_requirement_status(), make_prerequisites()
    )

    assert result.loc[0, "prereq_ready"] == "no"
    assert result.loc[0, "missing_prerequisites"] == "THE3000"


def test_readiness_output_columns_exist():
    # readiness output should keep the agreed intermediate schema.
    result = build_student_readiness_status(
        make_requirement_status(), make_prerequisites()
    )

    assert list(result.columns) == READINESS_COLUMNS
