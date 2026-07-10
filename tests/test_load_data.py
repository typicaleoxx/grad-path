# this file tests csv loading, required column checks, and course history combining.

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.load_data import (
    COURSE_COLUMNS,
    DEGREE_REQUIREMENT_COLUMNS,
    PREREQUISITE_COLUMNS,
    REQUIRED_FILES,
    STUDENT_COLUMNS,
    combine_course_history,
    load_all_data,
    validate_required_columns,
)


def write_csv(path, columns, rows=None):
    # write a small csv fixture with only the columns needed for the test.
    rows = rows or [{column: f"{column} value" for column in columns}]
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)


def create_raw_data_dir(tmp_path):
    # create a complete raw data folder in the temporary test area.
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    write_csv(
        raw_dir / REQUIRED_FILES["theatre_majors"],
        STUDENT_COLUMNS,
        [{"UID": "U00000001", **{column: "" for column in STUDENT_COLUMNS if column != "UID"}}],
    )

    course_rows = [
        {
            "Prefix": "THE",
            "Number": "2305.0",
            "Course Title": "Script Analysis",
            "Semester": "Fall 2024",
            "UID": "U00000001",
            "Name": "Student One",
            "Grade Mode": "Standard",
            "Credits": "3",
            "Final Grade Entered": "A",
            "Passing": "Y",
            "Passing Override": "",
        }
    ]

    for data_key in [
        "the_courses",
        "tpa_courses",
        "tpp_courses",
        "practicum_courses",
    ]:
        write_csv(raw_dir / REQUIRED_FILES[data_key], COURSE_COLUMNS, course_rows)

    write_csv(raw_dir / REQUIRED_FILES["degree_requirements"], DEGREE_REQUIREMENT_COLUMNS)
    write_csv(raw_dir / REQUIRED_FILES["prerequisites"], PREREQUISITE_COLUMNS)

    return raw_dir


def test_load_all_data_loads_required_files(tmp_path):
    # a complete raw folder should load into the expected dataframe dictionary.
    raw_dir = create_raw_data_dir(tmp_path)

    data = load_all_data(raw_dir)

    assert set(data) == set(REQUIRED_FILES)
    assert list(data["theatre_majors"].columns) == STUDENT_COLUMNS
    assert list(data["the_courses"].columns) == COURSE_COLUMNS


def test_load_all_data_raises_for_missing_file(tmp_path):
    # missing required inputs should fail before downstream work begins.
    raw_dir = create_raw_data_dir(tmp_path)
    (raw_dir / REQUIRED_FILES["prerequisites"]).unlink()

    with pytest.raises(FileNotFoundError, match="prerequisites.csv"):
        load_all_data(raw_dir)


def test_validate_required_columns_raises_for_missing_column(tmp_path):
    # column validation should name the dataset and column that caused the failure.
    raw_dir = create_raw_data_dir(tmp_path)
    write_csv(
        raw_dir / REQUIRED_FILES["theatre_majors"],
        STUDENT_COLUMNS[:-1],
    )

    data = {
        data_key: pd.read_csv(raw_dir / file_name, dtype=str)
        for data_key, file_name in REQUIRED_FILES.items()
    }

    with pytest.raises(ValueError, match="theatre_majors: missing columns Theatre Conc"):
        validate_required_columns(data)


def test_combine_course_history_adds_course_code_and_source_file(tmp_path):
    # combined course history should retain key course fields and show its source.
    raw_dir = create_raw_data_dir(tmp_path)
    data = load_all_data(raw_dir)

    combined = combine_course_history(data)

    assert len(combined) == 4
    assert "course_code" in combined.columns
    assert "source_file" in combined.columns
    assert combined.loc[0, "course_code"] == "THE2305"
    assert set(combined["source_file"]) == {
        "the_courses",
        "tpa_courses",
        "tpp_courses",
        "practicum_courses",
    }
    assert {"UID", "Prefix", "Number", "Course Title", "Credits", "Passing"}.issubset(
        combined.columns
    )
