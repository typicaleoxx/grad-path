# gradpath

## Project Description

gradpath is a course demand planning prototype that uses fake student records, degree requirements, prerequisites, and course offering data to estimate future course demand.

The goal is to help show how many students may need selected theatre courses in future semesters and which students may need priority access to stay on track for graduation.

This project uses fictional data only. It does not use real student records.

## Team Members

* Sneha Lama
* Christopher Pyfrom
* Joshua Smith

## How to Run the Project

### 1. Clone the Repository

```bash
git clone <repository-url>
cd grad-path
```

### 2. Build the Docker Image
The image's name is: **gradpath**.
```bash
docker build -t gradpath .
```

### 3. Build the Container from the Image
The container's name is: **gradpath-test**.
```bash
docker run --name gradpath-test -p 8501:8501 gradpath
```

### 4. Check the Output Files

The generated reports should appear inside the `outputs/` folder.

```text
outputs/course_demand_report.csv
outputs/priority_students.csv
```

#### Post-Intermediate Analytics

The post-intermediate analytics step starts from `data/intermediate/tap_intermediate_data.csv`. This file already contains each student's requirement status in a wide format. The project converts it into `student_readiness_status.csv`, then creates graduation progress, course demand, and priority student reports.

Input file:

```text
data/intermediate/tap_intermediate_data.csv
```

Generated files:

```text
data/intermediate/student_readiness_status.csv
outputs/student_graduation_summary.csv
outputs/course_demand_report.csv
outputs/priority_students.csv
```

To view the dashboard:

```bash
streamlit run app.py
```

### 5. Closing the program
Close the dashboard browser window. Then return to the terminal.

Enter [control]C:
```bash
^c
```


## Problem

Departments cannot always offer every course every semester. Some required courses are offered often, while upper-level or concentration-specific courses may be offered less often.

This can become a problem when students need a course to graduate on time, but the department does not have a quick way to estimate future demand.

Common methods include:

1. Checking previous enrollment numbers
2. Reviewing student degree audits manually

Previous enrollment numbers may not show future need accurately. Manual review may be more accurate, but it takes too much time.

gradpath tries to make this easier by using fake student data and course rules to estimate course demand.

## What the Project Does

Gradpath will:

1. Load (fake) student data
2. Load (fake) completed-course records
3. Load degree requirements
4. Load prerequisite rules
5. Compare completed courses with required courses
6. Identify missing required courses
7. Check whether prerequisites are complete
8. Estimate when each course may be needed
9. Create a course demand report
10. Create anonymized student priority groups

## Planned Stack

| part               | tool                |
| ------------------ | ------------------- |
| language           | python              |
| data format        | csv                 |
| data processing    | pandas              |
| logic              | rule-based planning |
| reports            | csv output          |
| optional dashboard | streamlit           |
| optional charts    | matplotlib          |

## Project Architecture

```text
fake csv data
      |
      v
data loading
      |
      v
data cleaning
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
demand aggregation
      |
      v
reports or dashboard
```

## Folder Structure

```text
gradpath/
│
├── data/
│   ├── intermediate/
│   │   ├── student_readiness_status.csv
│   │   ├── tap_intermediate_data.csv
│   │   └── tap_pre_intermediate_data.csv
│   │
│   ├── raw/
│   │   ├── Practicum_Courses.csv
│   │   ├── THE_Courses.csv
│   │   ├── TPA_Courses.csv
│   │   ├── TPP_Courses.csv
│   │   └── TheatreMajors.csv
│   │
│   └──  static/
│       ├── degree_requirements.csv
│       └── prerequisites.csv
│
├── dataGen/
│   ├── CourseList.xlsx
│   └── StudentDataBuilder.py
│
├── src/
│   ├── demand_report.py
│   ├── grad_dist.py
│   ├── load_data.py
│   ├── planner.py
│   ├── prerequisite_checker.py
│   └── utils.py
│
├── outputs/
│   ├── course_demand_report.csv
│   └── priority_students.csv
│
├── app.py
├── requirements.txt
├── README.md
└── PLANNING.md
```

## Data Files

### TheatreMajors.csv

Stores a list of theatre majors with fake student information.

Expected columns:

```csv
Term,Term Description,Last Name,First Name,UID,Count,Email,Camp,Coll,Dep 1,Levl,Prim Majr1,Prim Majr2,Seco Majr1,Seco Majr2,Minr1,Minr2,Prim Conc,Prim Conc2,Seco Conc,Seco Conc2,Class,Admit Term,Enrolled [Y/N],Stu Type,Student Type Description,Student Attribute,USF Earned Hours,Overall Earned Hours,USF GPA,Theatre Major,Theatre Conc
```

### THE_Courses.csv, TPA_Courses.csv, TPP_Courses.csv, Practicum_Courses.csv

Stores fake completed courses grouped by course prefix.

Expected columns:

```csv
Prefix,Number,Course Title,Section,CRN,Semester,UID,Name,Registration,Date,Midterm,Final,Grade Mode,Credits,Final Grade Entered,Passing,Passing Override
```

### degree_requirements.csv

Stores required courses by degree and concentration.

Expected columns:

```csv
Degree,Conc,Requirement,Course or Credit,Quantity,Courses Accepted
```

### prerequisites.csv

Stores prerequisite rules.

Expected columns:

```csv
Course,'(',Requisite,Min Grade,Concurrency,')',And/Or
```

## How the Logic Works

For each student, the system will:

1. Find the student’s concentration
2. Find the courses required for that concentration
3. Find the courses the student already completed
4. Compare completed courses with required courses
5. Identify missing courses
6. Check whether prerequisites are complete
7. Estimate when each course may be needed
8. Assign a priority level if needed

Example:

```text
student S001 completed:
THE 1000
THE 2000
THE 3100

Performance requirements:
THE 1000
THE 2000
THE 3100
THE 4200

Missing course:
THE 4200

THE 4200 requires THE 3100.
S001 completed THE 3100.
S001 may need THE 4200 within 1 semester.
priority: high
```

## Need Categories

| course <br> missing | prereq complete <br> or in-progress | min time to <br> graduation | steps from <br> course/capstone | needed in...    |
| :-------: | :-------------: | :-------------- | :-------------: | :-------------- |
| yes       | yes             | 1 semester      | 1/1             | 1 semester      |
| yes       | yes             | 2 semesters     | 1/2             | 1 semester      |
| yes       | yes             | 3 semesters     | 1/3             | 1 semester      |
| yes       | yes             | 4 semesters     | 1/4             | 1 semester      |
| yes       | yes             | 2 semesters     | 1/1             | 2 semesters     |
| yes       | no              | 2 semesters     | 2/2             | 2 semesters     |
| yes       | yes             | 3 semesters     | 1/2             | 2 semesters     |
| yes       | no              | 3 semesters     | 2/3             | 2 semesters     |
| yes       | no              | 4 semesters     | 2/4             | 2 semesters     |
| yes       | yes             | 3 semesters     | 1/1             | 3 semesters     |
| yes       | yes             | 4 semesters     | 1/2             | 3 semesters     |
| yes       | no              | 4 semesters     | 2/3             | 3 semesters     |
| yes       | no              | 4 semesters     | 3/4             | 3 semesters     |
| yes       | yes             | 5 semesters     | 1/3             | 3 semesters     |
| yes       | no              | 5 semesters     | 2/4             | 3 semesters     |
| yes       | yes             | 4+ semesters    | 1/1             | 4+ semesters    |
| yes       | yes             | 5+ semesters    | 1/2             | 4+ semesters    |
| yes       | no              | 5+ semesters    | 2/3             | 4+ semesters    |
| yes       | yes             | 6+ semesters    | 1/3             | 4+ semesters    |
| yes       | no              | 6+ semesters    | 2/4             | 4+ semesters    |

## Priority Levels

| priority | meaning                                                          |
| -------- | ---------------------------------------------------------------- |
| high     | prereq's are complete and course is needed within 2 semesters    |
| medium   | prereq's are complete and course is needed within 3 semesters    |
| low      | prereq's are complete and course is needed in 4+ semesters       |
| none     | course is required but another course must be completed first    |

## Expected Outputs

### course_demand_report.csv

This report shows how many students may need each course.

Example columns:

```csv
course_code,needed_1_semester,needed_2_semesters,needed_3_semesters,needed_4_plus_semesters,total_demand
```

### priority_students.csv

This report shows anonymized students who may need priority.

Example columns:

```csv
student_id,course_code,priority,reason
```

## Dashboard

To open the dashboard, run:

```bash
streamlit run app.py
```

The dashboard shows:

1. Course demand summary
2. Student priority groups
3. Filter by course
4. Filter by concentration
5. Chart of demand by course

## Project Scope

This project will focus on:

1. Fake theatre student data
2. Selected required theatre courses
3. Prerequisite checking
4. Estimated course need categories
5. Course demand reports
6. Anonymized priority groups

This project will not:

1. Use real student data
2. Replace degreeworks
3. Replace academic advisors
4. Register students
5. Create full student schedules
6. Assign instructors
7. Assign classrooms
8. Predict grades

## Current Status

Current Features:

* [x] Create fake csv data
* [x] Load data with pandas
* [x] Clean course codes and records
* [x] Match students to degree requirements
* [x] Identify missing courses
* [x] Check prerequisites
* [x] Estimate course need categories
* [x] Generate course demand report
* [x] Generate priority student report
* [x] Add Streamlit Dashboard
* [ ] Containerize the application with Docker
* [ ] Add Docker build and run documentation

## Final Goal

The final goal is to create a working prototype that shows how course history, degree requirements, prerequisites, and course offering data can be used to estimate future course demand.

gradpath is meant to support department planning by producing clear course demand counts and student priority groups from fake data.
