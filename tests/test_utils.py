# this file tests the small cleaning helpers used by the data loader.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import (
    build_course_code,
    clean_course_number,
    clean_student_id,
    normalize_text,
)


def test_clean_student_id_strips_spaces_and_uppercases():
    # student ids should be stable for joins even when source spacing changes.
    assert clean_student_id(" u00000001 ") == "U00000001"


def test_clean_course_number_removes_decimal_suffix():
    # excel-style csv exports can turn course numbers into decimal-looking text.
    assert clean_course_number("2305.0") == "2305"


def test_build_course_code_combines_prefix_and_number():
    # course codes are matched without a space between subject and number.
    assert build_course_code("the", "2305") == "THE2305"


def test_normalize_text_strips_lowercases_and_collapses_spaces():
    # text normalization keeps comparisons simple for labels and descriptions.
    assert normalize_text("  Theatre Arts  ") == "theatre arts"
