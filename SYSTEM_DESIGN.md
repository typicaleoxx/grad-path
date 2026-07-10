# GradPath System Design

## Purpose

This document explains the system design for GradPath. It describes the folder structure, data flow, main processing steps, intermediate files, final outputs, and how each part of the project connects.

GradPath is a course demand planning prototype. It uses sample student records, course history files, degree requirements, and prerequisite rules to estimate future course demand and identify students who may need priority access to required courses.

The system does not replace DegreeWorks, academic advisors, or department scheduling decisions. It only creates planning reports from structured project data.

## System Overview

GradPath follows a simple data pipeline design.

```text
raw data
   |
   v
data loading
   |
   v
data cleaning
   |
   v
course history aggregation
   |
   v
requirement matching
   |
   v
prerequisite checking
   |
   v
course need estimation
   |
   v
final reports
   |
   v
optional dashboard
```

The main idea is to take separate input files and turn them into clear reports.

The system starts with raw CSV files in `data/raw/`. These files are loaded and cleaned by Python scripts in `src/`. The cleaned working files are saved in `data/intermediate/`. Final reports are saved in `outputs/`.

## Folder Structure

```text
grad-path/
|
├── data/
|   ├── raw/
|   |   ├── Train01_TheatreMajors.csv
|   |   ├── Train01_THE_Courses.csv
|   |   ├── Train01_TPA_Courses.csv
|   |   ├── Train01_TPP_Courses.csv
|   |   ├── Train01_Practicum_Courses.csv
|   |   ├── degree_requirements.csv
|   |   └── prerequisites.csv
|   |
|   └── intermediate/
|       ├── student_course_status.csv
|       ├── student_requirement_status.csv
|       └── student_readiness_status.csv
|
├── outputs/
|   ├── course_demand_report.csv
|   └── priority_students.csv
|
├── dataGen/
|   ├── CourseList.xlsx
|   └── StudentDataBuilder_csv.py
|
├── src/
|   ├── load_data.py
|   ├── utils.py
|   ├── planner.py
|   └── demand_report.py
|
├── tests/
|   ├── test_load_data.py
|   └── test_utils.py
|
├── app.py
├── requirements.txt
├── README.md
├── PLANNING.md
├── SYSTEM_DESIGN.md
├── LICENSE
└── .gitignore
```

## Folder Responsibilities

| Folder or File | Purpose |
| --- | --- |
| `data/raw/` | stores the original project CSV files |
| `data/intermediate/` | stores cleaned working files created during processing |
| `outputs/` | stores final generated reports |
| `dataGen/` | stores files used to create or regenerate the sample dataset |
| `src/` | stores the main Python project logic |
| `tests/` | stores automated tests |
| `app.py` | optional Streamlit dashboard |
| `requirements.txt` | lists project dependencies |
| `README.md` | explains the project and how to run it |
| `PLANNING.md` | explains the project plan and phases |
| `SYSTEM_DESIGN.md` | explains the system architecture and data flow |

## Main Data Files

### `Train01_TheatreMajors.csv`

This file contains the main student list.

It includes student-level information such as:

- student id
- major
- concentration
- class level
- admit term
- earned hours
- GPA
- enrollment status

This file tells the system which students are included in the project.

### Course History Files

These files contain course records grouped by course prefix or course type:

```text
Train01_THE_Courses.csv
Train01_TPA_Courses.csv
Train01_TPP_Courses.csv
Train01_Practicum_Courses.csv
```

They include information such as:

- student id
- course prefix
- course number
- course title
- credits
- grade mode
- passing status
- final grade status

These files tell the system which courses each student has completed or started.

### `degree_requirements.csv`

This file stores degree and concentration requirements.

It includes information such as:

- degree
- concentration
- requirement name
- course or credit requirement
- required quantity
- accepted courses

This file tells the system what each student needs to complete.

### `prerequisites.csv`

This file stores prerequisite rules.

It includes information such as:

- target course
- prerequisite course
- minimum grade
- concurrency rule
- AND or OR logic

This file tells the system whether a student is ready to take a missing course.

## Data Flow

```text
data/raw/
   |
   v
load_data.py
   |
   v
utils.py
   |
   v
planner.py
   |
   v
data/intermediate/
   |
   v
demand_report.py
   |
   v
outputs/
   |
   v
app.py optional
```

## Step 1: Data Loading

File:

```text
src/load_data.py
```

Purpose:

Load all required CSV files from `data/raw/`.

This file should:

1. check that required files exist
2. read CSV files into pandas dataframes
3. check that important columns exist
4. return the loaded data in a clear structure

Expected loaded data keys:

```text
theatre_majors
the_courses
tpa_courses
tpp_courses
practicum_courses
degree_requirements
prerequisites
```

This step does not make final decisions. It only prepares the data for the rest of the system.

## Step 2: Utility Cleaning

File:

```text
src/utils.py
```

Purpose:

Store helper functions used by multiple files.

Examples of helper functions:

```text
clean_student_id()
clean_course_number()
build_course_code()
normalize_text()
```

These functions keep formatting consistent.

Example:

```text
prefix: THE
number: 2305

course_code: THE2305
```

This matters because the system needs course codes to match across course history files, degree requirements, and prerequisites.

## Step 3: Course History Aggregation

Input files:

```text
Train01_THE_Courses.csv
Train01_TPA_Courses.csv
Train01_TPP_Courses.csv
Train01_Practicum_Courses.csv
```

Output file:

```text
data/intermediate/student_course_status.csv
```

Purpose:

Combine all course history files into one clean table.

Example output:

```csv
student_id,course_code,course_title,status,credits,source_file
U00000001,THE2305,Script Analysis,complete,3,Train01_THE_Courses.csv
U00000002,TPA2200,Intro to Technical Theatre,in_progress,3,Train01_TPA_Courses.csv
```

This intermediate file helps the system avoid checking many separate course files every time.

## Step 4: Requirement Matching

Input files:

```text
data/raw/Train01_TheatreMajors.csv
data/raw/degree_requirements.csv
data/intermediate/student_course_status.csv
```

Output file:

```text
data/intermediate/student_requirement_status.csv
```

Purpose:

Compare each student's completed courses with their degree and concentration requirements.

The system checks:

1. what major the student is in
2. what concentration the student is in
3. what requirements apply to that student
4. which requirements are complete
5. which requirements are in progress
6. which requirements are still missing

Example output:

```csv
student_id,degree,concentration,requirement,accepted_courses,status,matched_course
U00000001,TAR,TAP,History Elective,"THE3110,THE3111",complete,THE3110
U00000001,TAR,TAP,Advanced Theatre Course,"THE4562",missing,
```

Status values may include:

| Status | Meaning |
| --- | --- |
| `complete` | student has completed the requirement |
| `in_progress` | student is currently taking a course that may satisfy it |
| `missing` | student has not completed the requirement |
| `ready` | student is missing the course but prerequisites appear complete |
| `not_ready` | student is missing the course and prerequisites are not complete |

## Step 5: Prerequisite Checking

Input files:

```text
data/raw/prerequisites.csv
data/intermediate/student_course_status.csv
data/intermediate/student_requirement_status.csv
```

Output file:

```text
data/intermediate/student_readiness_status.csv
```

Purpose:

Check whether a student is ready to take each missing course.

The system checks:

1. which course is missing
2. whether that course has prerequisites
3. whether the student completed the prerequisites
4. whether the student is ready or blocked

Example output:

```csv
student_id,course_code,prereq_ready,missing_prerequisites,reason
U00000001,THE4562,no,"THE3110","student has not completed prerequisite"
U00000002,THE4562,yes,"","prerequisites complete"
```

## Step 6: Course Need Estimation

File:

```text
src/planner.py
```

Purpose:

Estimate when a student may need each missing course.

The system may consider:

1. whether the course is required
2. whether prerequisites are complete
3. how many semesters the student may have left
4. how close the course is to later requirements or capstone courses
5. whether the course is usually offered soon

Possible need categories:

| Category | Meaning |
| --- | --- |
| `needed_1_semester` | course may be needed very soon |
| `needed_2_semesters` | course may be needed soon |
| `needed_3_semesters` | course may be needed later |
| `needed_4_plus_semesters` | course is a longer-term need |

## Step 7: Priority Assignment

File:

```text
src/planner.py
```

Purpose:

Assign a priority level to students for missing courses.

Suggested priority logic:

| Priority | Meaning |
| --- | --- |
| `high` | prerequisites are complete and course is needed within two semesters |
| `medium` | prerequisites are complete and course is needed within three semesters |
| `low` | prerequisites are complete but course is needed later |
| `none` | course is required but prerequisites are not complete yet |

Priority groups are not final decisions. They are only planning signals.

## Step 8: Final Report Generation

File:

```text
src/demand_report.py
```

Purpose:

Create final output reports from the intermediate data.

Final report 1:

```text
outputs/course_demand_report.csv
```

This report shows how many students may need each course.

Example:

```csv
course_code,needed_1_semester,needed_2_semesters,needed_3_semesters,needed_4_plus_semesters,total_demand
THE4562,5,8,3,2,18
```

Final report 2:

```text
outputs/priority_students.csv
```

This report shows which students may need priority.

Example:

```csv
student_id,course_code,priority,reason
U00000001,THE4562,high,prerequisites complete and course is needed soon
```

## Optional Dashboard

File:

```text
app.py
```

Purpose:

Display the final reports in a simple visual format.

The dashboard may show:

1. course demand report
2. priority student report
3. filters by course
4. filters by concentration
5. bar chart of demand by course

The dashboard should only be added after the report files are working.

## System Flow Diagram

```text
+----------------------+
| data/raw             |
| raw sample csv files |
+----------+-----------+
           |
           v
+----------------------+
| load_data.py         |
| load and validate    |
+----------+-----------+
           |
           v
+----------------------+
| utils.py             |
| clean ids and codes  |
+----------+-----------+
           |
           v
+----------------------+
| planner.py           |
| match requirements   |
| check prerequisites  |
| estimate course need |
+----------+-----------+
           |
           v
+----------------------+
| data/intermediate    |
| cleaned working data |
+----------+-----------+
           |
           v
+----------------------+
| demand_report.py     |
| create final reports |
+----------+-----------+
           |
           v
+----------------------+
| outputs              |
| final csv reports    |
+----------+-----------+
           |
           v
+----------------------+
| app.py optional      |
| dashboard view       |
+----------------------+
```

## Data State Definitions

| Data State | Location | Meaning |
| --- | --- | --- |
| raw data | `data/raw/` | original sample input files |
| intermediate data | `data/intermediate/` | cleaned working files created by the system |
| final output | `outputs/` | final reports used for the demo |

## Main Outputs

### Course Demand Report

Answers:

```text
how many students may need each course?
```

Expected file:

```text
outputs/course_demand_report.csv
```

### Priority Students Report

Answers:

```text
which students may need priority access and why?
```

Expected file:

```text
outputs/priority_students.csv
```

## Testing Plan

The project should include tests for the first technical pieces.

Test files:

```text
tests/test_load_data.py
tests/test_utils.py
```

Tests should check:

1. CSV files can be loaded
2. missing files are handled correctly
3. required columns are checked
4. course codes are cleaned consistently
5. student ids are cleaned consistently
6. course history files can be combined

Later tests can check:

1. requirement matching
2. prerequisite readiness
3. need category assignment
4. report generation

## Build Order

The system should be built in this order:

1. set up folder structure
2. move raw data into `data/raw/`
3. create `requirements.txt`
4. build `src/load_data.py`
5. build `src/utils.py`
6. write tests for loading and cleaning
7. create `data/intermediate/student_course_status.csv`
8. create requirement matching logic
9. create prerequisite checking logic
10. create course need estimation logic
11. generate final reports
12. add optional dashboard

## Design Limits

GradPath will not:

1. use real student records
2. replace DegreeWorks
3. replace academic advisors
4. register students
5. create full student schedules
6. assign instructors
7. assign classrooms
8. predict grades
9. handle login or user accounts
10. build a full university scheduling system

## Summary

GradPath is designed as a small data pipeline. It starts with sample course and student data, cleans and combines the data, checks requirements and prerequisites, creates intermediate working files, and generates final course demand and priority reports.

The design keeps the project manageable while still showing how student records, degree requirements, and prerequisite rules can support course planning.
