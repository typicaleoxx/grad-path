# this file holds small cleaning helpers used while loading student and course data.

import pandas as pd


def normalize_text(value):
    # normalize free text so matching is less sensitive to casing and spacing.
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    return " ".join(text.split())


def clean_student_id(value):
    # standardize student ids from reports before joining tables.
    if pd.isna(value):
        return ""

    return str(value).strip().upper()


def clean_course_number(value):
    # remove spreadsheet-style decimal endings from course numbers.
    if pd.isna(value):
        return ""

    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]

    return text


def build_course_code(prefix, number):
    # combine prefix and number into the compact course code used in requirements.
    clean_prefix = str(prefix).strip().upper() if not pd.isna(prefix) else ""
    clean_number = clean_course_number(number)

    return f"{clean_prefix}{clean_number}"
