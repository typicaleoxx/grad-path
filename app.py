# this file displays demand, priority, and graduation progress analytics.

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FILES = {
    "requirement_status": (
        PROJECT_ROOT / "data" / "intermediate" / "student_requirement_status.csv"
    ),
    "readiness_status": (
        PROJECT_ROOT / "data" / "intermediate" / "student_readiness_status.csv"
    ),
    "course_demand": PROJECT_ROOT / "outputs" / "course_demand_report.csv",
    "priority_students": PROJECT_ROOT / "outputs" / "priority_students.csv",
    "graduation_summary": (
        PROJECT_ROOT / "outputs" / "student_graduation_summary.csv"
    ),
}


@st.cache_data
def load_csv(path):
    # cache report reads so dashboard filters stay responsive.
    return pd.read_csv(Path(path), dtype=str).fillna("")


def load_dashboard_data():
    # load each required pipeline file under a short dashboard key.
    return {name: load_csv(path) for name, path in DATA_FILES.items()}


def show_missing_files(missing_files):
    # name missing files and provide the two commands that rebuild this layer.
    st.error("The following dashboard files are missing:")
    for path in missing_files:
        st.code(str(path.relative_to(PROJECT_ROOT)))
    st.write("Run these commands from the project root:")
    st.code("python src/prerequisite_checker.py\npython src/demand_report.py")


def filter_table(data, column, label):
    # use an all option so each filter can be cleared without resetting the page.
    options = ["All"] + sorted(value for value in data[column].unique() if value)
    selected = st.selectbox(label, options)
    if selected == "All":
        return data
    return data[data[column] == selected]


def show_overview(data):
    # summarize the main workload and student progress signals.
    graduation = data["graduation_summary"].copy()
    demand = data["course_demand"].copy()
    priority = data["priority_students"]
    readiness = data["readiness_status"]
    graduation["completion_percent"] = pd.to_numeric(
        graduation["completion_percent"], errors="coerce"
    ).fillna(0)

    metrics = st.columns(6)
    metrics[0].metric("Total students", graduation["student_id"].nunique())
    metrics[1].metric("Total demanded courses", demand["course_code"].nunique())
    metrics[2].metric("High priority rows", priority["priority"].eq("high").sum())
    metrics[3].metric(
        "Ready missing courses", readiness["prereq_ready"].eq("yes").sum()
    )
    metrics[4].metric(
        "Blocked missing courses", readiness["prereq_ready"].eq("no").sum()
    )
    metrics[5].metric(
        "Average completion percent",
        f"{graduation['completion_percent'].mean():.2f}%",
    )


def show_course_demand(data):
    # compare total and near-term demand across course codes.
    demand = data["course_demand"].copy()
    numeric_columns = [
        "needed_1_semester",
        "needed_2_semesters",
        "needed_3_semesters",
        "needed_4_plus_semesters",
        "total_demand",
    ]
    demand[numeric_columns] = demand[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    ).fillna(0)
    top_demand = demand.sort_values("total_demand", ascending=False).head(10)

    st.dataframe(demand, hide_index=True, width="stretch")
    st.subheader("Top demanded courses")
    st.dataframe(top_demand, hide_index=True, width="stretch")

    chart_data = demand.set_index("course_code")
    st.subheader("Total demand by course")
    st.bar_chart(chart_data["total_demand"])
    st.subheader("Needed in 1 semester")
    st.bar_chart(chart_data["needed_1_semester"])
    st.subheader("Needed in 2 semesters")
    st.bar_chart(chart_data["needed_2_semesters"])


def show_graduation_progress(data):
    # filter student progress before displaying the table and charts.
    graduation = data["graduation_summary"].copy()
    graduation["missing_requirements"] = pd.to_numeric(
        graduation["missing_requirements"], errors="coerce"
    ).fillna(0)
    graduation["completion_percent"] = pd.to_numeric(
        graduation["completion_percent"], errors="coerce"
    ).fillna(0)

    filters = st.columns(3)
    with filters[0]:
        graduation = filter_table(
            graduation, "graduation_status", "Graduation status"
        )
    with filters[1]:
        graduation = filter_table(graduation, "degree", "Degree")
    with filters[2]:
        graduation = filter_table(graduation, "concentration", "Concentration")

    st.dataframe(graduation, hide_index=True, width="stretch")
    if not graduation.empty:
        chart_data = graduation.set_index("student_id")
        st.subheader("Missing requirements by student")
        st.bar_chart(chart_data["missing_requirements"])
        st.subheader("Completion percent by student")
        st.bar_chart(chart_data["completion_percent"])


def show_student_detail(data):
    # show progress metrics and requirement tables for one selected student.
    graduation = data["graduation_summary"]
    requirement_status = data["requirement_status"]
    readiness_status = data["readiness_status"]
    student_id = st.selectbox(
        "Student ID", sorted(graduation["student_id"].unique())
    )
    student = graduation[graduation["student_id"] == student_id].iloc[0]

    details = st.columns(4)
    details[0].metric("Degree", student["degree"])
    details[1].metric("Concentration", student["concentration"] or "None")
    details[2].metric("Completion percent", f"{student['completion_percent']}%")
    details[3].metric("Graduation status", student["graduation_status"])

    counts = st.columns(5)
    for column, label, metric in [
        ("complete_requirements", "Complete", counts[0]),
        ("in_progress_requirements", "In progress", counts[1]),
        ("missing_requirements", "Missing", counts[2]),
        ("ready_missing_requirements", "Ready missing", counts[3]),
        ("blocked_missing_requirements", "Blocked missing", counts[4]),
    ]:
        metric.metric(label, student[column])

    student_requirements = requirement_status[
        requirement_status["student_id"] == student_id
    ]
    for status, heading in [
        ("complete", "Complete requirements"),
        ("in_progress", "In progress requirements"),
        ("missing", "Missing requirements"),
    ]:
        st.subheader(heading)
        st.dataframe(
            student_requirements[student_requirements["status"] == status],
            hide_index=True,
            width="stretch",
        )

    st.subheader("Prerequisite readiness")
    st.dataframe(
        readiness_status[readiness_status["student_id"] == student_id],
        hide_index=True,
        width="stretch",
    )


def show_priority_students(data):
    # filter priority rows by the fields used during planning review.
    priority = data["priority_students"]
    filters = st.columns(3)
    with filters[0]:
        priority = filter_table(priority, "priority", "Priority")
    with filters[1]:
        priority = filter_table(priority, "course_code", "Course code")
    with filters[2]:
        priority = filter_table(priority, "student_id", "Student ID")
    st.dataframe(priority, hide_index=True, width="stretch")


def show_raw_previews(data):
    # keep full pipeline tables available without crowding the main sections.
    labels = {
        "requirement_status": "student_requirement_status.csv",
        "readiness_status": "student_readiness_status.csv",
        "course_demand": "course_demand_report.csv",
        "priority_students": "priority_students.csv",
        "graduation_summary": "student_graduation_summary.csv",
    }
    for key, label in labels.items():
        with st.expander(label):
            st.dataframe(data[key], hide_index=True, width="stretch")


def main():
    # load the complete analytics layer before rendering dashboard sections.
    st.set_page_config(page_title="GradPath Dashboard", layout="wide")
    st.title("GradPath Dashboard")
    missing_files = [path for path in DATA_FILES.values() if not path.exists()]
    if missing_files:
        show_missing_files(missing_files)
        return

    data = load_dashboard_data()
    st.header("Overview summary")
    show_overview(data)
    st.header("Course demand analytics")
    show_course_demand(data)
    st.header("Student graduation progress")
    show_graduation_progress(data)
    st.header("Student detail view")
    show_student_detail(data)
    st.header("Priority students")
    show_priority_students(data)
    st.header("Raw data previews")
    show_raw_previews(data)


if __name__ == "__main__":
    main()
