# this file displays a small streamlit preview of the course status dataset.

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "intermediate"
    / "student_course_status.csv"
)


def load_course_status(path=DATA_PATH):
    # read the generated intermediate file without changing its values.
    return pd.read_csv(Path(path), dtype=str).fillna("")


def build_count_table(data, column, label):
    # turn value counts into a clear two-column dashboard table.
    return (
        data[column]
        .value_counts(dropna=False)
        .rename_axis(label)
        .reset_index(name="records")
    )


def show_dashboard(data):
    # summarize the course records before showing detailed tables.
    status_counts = data["status"].value_counts()
    summary_columns = st.columns(4)
    summary_columns[0].metric("Total course records", len(data))
    summary_columns[1].metric("Complete", status_counts.get("complete", 0))
    summary_columns[2].metric("In progress", status_counts.get("in_progress", 0))
    summary_columns[3].metric("Unknown", status_counts.get("unknown", 0))

    # show compact counts for the two main record groupings.
    st.subheader("Course prefix counts")
    st.dataframe(
        build_count_table(data, "course_prefix", "course_prefix"),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Status counts")
    st.dataframe(
        build_count_table(data, "status", "status"),
        hide_index=True,
        use_container_width=True,
    )

    # keep the preview short enough to scan in the browser.
    st.subheader("Course record preview")
    st.dataframe(data.head(50), hide_index=True, use_container_width=True)


def main():
    # stop with a useful instruction when the pipeline has not run yet.
    st.set_page_config(page_title="GradPath Data Preview", layout="wide")
    st.title("GradPath Data Preview")

    if not DATA_PATH.exists():
        st.warning("Course status data was not found. Run `python src/planner.py`.")
        return

    show_dashboard(load_course_status())


if __name__ == "__main__":
    main()
