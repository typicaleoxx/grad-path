# streamlit dashboard for gradpath analytics reports.

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
FILES = {
    "readiness": ROOT / "data" / "intermediate" / "student_readiness_status.csv",
    "summary": ROOT / "outputs" / "student_graduation_summary.csv",
    "demand": ROOT / "outputs" / "course_demand_report.csv",
    "priority": ROOT / "outputs" / "priority_students.csv",
}


@st.cache_data
def load_csv(path):
    return pd.read_csv(path)


def missing_files():
    return [path for path in FILES.values() if not path.exists()]


def load_data():
    return {name: load_csv(path) for name, path in FILES.items()}


def show_missing_file_message(paths):
    st.error("missing dashboard data files")
    st.write("run these commands first:")
    st.code("python src/prerequisite_checker.py\npython src/demand_report.py", language="bash")
    for path in paths:
        st.write(f"missing: {path.relative_to(ROOT)}")


def metric_row(metrics):
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics):
        column.metric(label, value)


def filter_options(df, column):
    return sorted(df[column].dropna().unique().tolist())


def apply_multiselect_filter(df, column, label):
    values = st.multiselect(label, filter_options(df, column))
    if not values:
        return df
    return df[df[column].isin(values)]


def show_overview(summary_df, priority_df):
    st.header("1. overview")
    total_missing = int(summary_df["missing_requirements"].sum())
    ready_missing = int(summary_df["ready_missing_requirements"].sum())
    blocked_missing = int(summary_df["blocked_missing_requirements"].sum())
    average_completion = round(summary_df["completion_percent"].mean(), 2)
    high_priority = int((priority_df["priority"] == "high").sum())

    metric_row(
        [
            ("total students", len(summary_df)),
            ("total missing requirements", total_missing),
            ("ready missing requirements", ready_missing),
            ("blocked missing requirements", blocked_missing),
            ("average completion percent", average_completion),
            ("high priority rows", high_priority),
        ]
    )


def show_course_demand(demand_df):
    st.header("2. course demand analytics")
    st.subheader("course demand report")
    st.dataframe(demand_df, use_container_width=True)

    st.subheader("top demanded requirements")
    st.dataframe(demand_df.head(10), use_container_width=True)

    st.subheader("total demand by requirement")
    st.bar_chart(demand_df.set_index("requirement")["total_demand"])

    st.subheader("needed within 1 semester")
    st.bar_chart(demand_df.set_index("requirement")["needed_1_semester"])

    st.subheader("needed within 2 semesters")
    st.bar_chart(demand_df.set_index("requirement")["needed_2_semesters"])

    st.subheader("ready vs blocked students")
    st.bar_chart(demand_df.set_index("requirement")[["ready_students", "blocked_students"]])


def show_graduation_progress(summary_df):
    st.header("3. student graduation progress")
    filtered = summary_df.copy()
    filtered = apply_multiselect_filter(filtered, "degree", "degree")
    filtered = apply_multiselect_filter(filtered, "concentration", "concentration")
    filtered = apply_multiselect_filter(filtered, "graduation_status", "graduation status")

    st.dataframe(filtered, use_container_width=True)
    st.subheader("completion percent by student")
    st.bar_chart(filtered.set_index("student_id")["completion_percent"])

    st.subheader("missing requirements by student")
    st.bar_chart(filtered.set_index("student_id")["missing_requirements"])

    st.subheader("graduation status counts")
    st.bar_chart(filtered["graduation_status"].value_counts())


def show_individual_student(summary_df, readiness_df):
    st.header("4. individual student view")
    student_ids = filter_options(summary_df, "student_id")
    if not student_ids:
        st.info("no students available")
        return

    student_id = st.selectbox("student_id", student_ids)
    student = summary_df[summary_df["student_id"] == student_id].iloc[0]
    student_rows = readiness_df[readiness_df["student_id"] == student_id]

    metric_row(
        [
            ("completion percent", student["completion_percent"]),
            ("complete requirements", student["complete_requirements"]),
            ("in progress requirements", student["in_progress_requirements"]),
            ("missing requirements", student["missing_requirements"]),
            ("ready missing requirements", student["ready_missing_requirements"]),
            ("blocked missing requirements", student["blocked_missing_requirements"]),
        ]
    )

    st.write(
        {
            "student_name": student["student_name"],
            "degree": student["degree"],
            "concentration": student["concentration"],
            "class_year": student["class_year"],
            "overall_earned_hours": student["overall_earned_hours"],
            "gpa": student["gpa"],
            "graduation_status": student["graduation_status"],
        }
    )

    for title, status in [
        ("complete requirements", "complete"),
        ("in-progress requirements", "in_progress"),
        ("ready missing requirements", "missing_ready"),
        ("blocked missing requirements", "missing_blocked"),
    ]:
        st.subheader(title)
        st.dataframe(
            student_rows[student_rows["need_status"] == status], use_container_width=True
        )


def show_priority_students(priority_df):
    st.header("5. priority students")
    filtered = priority_df.copy()
    filtered = apply_multiselect_filter(filtered, "priority", "priority")
    filtered = apply_multiselect_filter(filtered, "requirement", "requirement")
    filtered = apply_multiselect_filter(filtered, "student_id", "student_id")
    st.dataframe(filtered, use_container_width=True)


def show_data_previews(data):
    st.header("6. data previews")
    names = {
        "readiness": "student_readiness_status.csv",
        "summary": "student_graduation_summary.csv",
        "demand": "course_demand_report.csv",
        "priority": "priority_students.csv",
    }
    for key, label in names.items():
        with st.expander(label):
            st.dataframe(data[key].head(50), use_container_width=True)


def main():
    st.set_page_config(page_title="GradPath Dashboard", layout="wide")
    st.title("GradPath Dashboard")

    paths = missing_files()
    if paths:
        show_missing_file_message(paths)
        return

    data = load_data()

    # render each dashboard section from the existing report csvs.
    show_overview(data["summary"], data["priority"])
    show_course_demand(data["demand"])
    show_graduation_progress(data["summary"])
    show_individual_student(data["summary"], data["readiness"])
    show_priority_students(data["priority"])
    show_data_previews(data)


if __name__ == "__main__":
    main()
