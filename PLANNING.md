# GradPath planningdocument

## project name

**gradpath: predicting student course needs**

## description

gradpath is a course planing prototype that uses student records, degree requirements, prerequisites, and course offering data to estimate future course demand and identify students who may need priority access to required courses.

## project goal

the goal of this project is to build a small working prototype that helps estimate which theatre courses students may need in future semesters.

this project is not meant to replace degreeworks, advisors, or department scheduling decisions. it is only meant to create a simple planning report based on student data and course requirement rules.

## main problem

departments cannot always offer every course every semester. some courses have enough enrollment to be offered often, while upper-level or concentration-specific courses may be offered less often.

this can create a problem when students need a required course to stay on track for graduation, but the department does not have a fast way to estimate future demand.

right now, course need can be estimated by:

1. looking at previous enrollment numbers
2. reviewing each student’s degreeworks audit manually

previous enrollment numbers are easy to check, but they may not show true future need. manual review can be more accurate, but it takes too much time.

gradpath will try to make this process easier by using student records and course requirement data to estimate course demand.

## what we are building

we are building a python-based course demand planning prototype.

the system will:

1. load student data
2. load completed-course records
3. load degree requirement data
4. load prerequisite rules
5. compare completed courses with required courses
6. find missing required courses
7. check whether prerequisites are complete
8. estimate when each course may be needed
9. combine the results into a course demand report
10. create anonymized student priority groups

## what we are not building

gradpath will not:

1. register students for courses
2. create complete student schedules
3. assign instructors
4. assign classrooms
5. predict student grades
6. replace academic advisors
7. replace degreeworks
8. handle login or user accounts
9. build a full university scheduling system

## planned stack

| area                 | tool                |
| -------------------- | ------------------- |
| programming language | python              |
| data format          | csv                 |
| data processing      | pandas              |
| planning logic       | rule based planning |
| reports              | csv output          |
| optional dashboard   | streamlit           |
| optional charts      | matplotlib          |
| version control      | github              |

## why this stack

python is a good choice because it is simple for data processing and easy to explain for this project.

csv files are enough at this prototype phase. we do not need a database for the first version. future versions that will use actual student data will need to be updated or regenertated each semester and will need to consider FERPA compliant data storage.

pandas will help us load, clean, filter, and group the data.

rule-based planning makes more sense than starting with machine learning because the dataset is small. the rules are also easier to explain and debug.

streamlit can be added later if we want a simple dashboard.

## project architecture

```text
csv data
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
reports or optional dashboard
```

## data files

the project will use fake csv files inside the `data/` folder.

### 1. TheatreMajors.csv

stores a list of theatre majors with fake student information.

expected columns:

```csv
Term,Term Description,Last Name,First Name,UID,Count,Email,Camp,Coll,Dep 1,Levl,Prim Majr1,Prim Majr2,Seco Majr1,Seco Majr2,Minr1,Minr2,Prim Conc,Prim Conc2,Seco Conc,Seco Conc2,Class,Admit Term,Enrolled [Y/N],Stu Type,Student Type Description,Student Attribute,USF Earned Hours,Overall Earned Hours,USF GPA,Theatre Major,Theatre Conc
```

example:

```csv
202608,Fall 2026,Student 1,Student 1,U00000001,1,,T,DP,TRD,UG,MTR,,,,,,,,,,4,202305,Y,B,"Beginner,First time in college",,90,107,3.8,MTR,
202608,Fall 2026,Student 2,Student 2,U00000002,1,,T,DP,TRD,UG,TAR,,,,,,TAA,,,,1,202608,Y,B,"Beginner,First time in college",,0,8,3.33,TAR,TAA
202608,Fall 2026,Student 3,Student 3,U00000003,1,,T,DP,TRD,UG,TAR,,,,,,TAP,,,,3,202401,Y,B,"Beginner,First time in college",,81,81,3.39,TAR,TAP
```

columns relevant to the problem:

```csv
Term,Last Name,First Name,UID,Class,Admit Term,Stu Type,USF Earned Hours,Overall Earned Hours,USF GPA,Theatre Major,Theatre Conc
```

definitions:
Term: 202608      yyyyss, yy=year, ss=semester code (01=Spring, 05=Summer, 08=Fall)
UID               university ID number, begins with 'U' followed by 8 digits
Class             year in school (1=year 1, 2 = year 2, etc.)
Admit Term        term student began at the current university in yyyyss format above
Stu Type          B=Beginner,First time in college; J=Transfer from FL Comm. College
Theatre Major     major (MTR=musical theatre, TAR=theatre)
Theatre Conc      concentration within major, only applies to TAR major (TAP=performance, 
                  TAA=theatre arts, TDAT=theatre design and technology)



### 2. THE_Courses.csv, TPA_Courses.csv, TPP_Courses.csv, Practicum_Courses.csv

stores fake completed courses grouped by course prefix.

expected columns:

```csv
Prefix,Number,Course Title,Section,CRN,Semester,UID,Name,Registration,Date,Midterm,Final,Grade Mode,Credits,Final Grade Entered,Passing,Passing Override
```

example:

```csv
THE,2305,Script Analysis,,,,U00000002,Student 2,,,,B,R,3,Y,c,
THE,3110,Theatre History 1,,,,U00000002,Student 2,,,,B,R,3,Y,c,
THE,4434,Caribbean Theatre,,,,U00000002,Student 2,,,,,R,3,N,ip,
```

columns relevant to the problem:
```csv
Prefix,Number,Course Title,UID,Name,Final,Grade Mode,Credits,Passing
```

definitions:
Prefix            theatre course prefixes (ex: THE, TPA, TPP)
UID               university ID number, begins with 'U' followed by 8 digits
Grade Mode        grade mode for course (R-regular, S=satisfactory/unsatisfactory)
Credits           credit hours earned for the course
Passing           passing status of the course completion (c=complete, ip=in progress)



### 3. degree_requirements.csv

stores required courses by degree and concentration.

expected columns:

```csv
Degree,Conc,Requirement,Course or Credit,Quantity,Courses Accepted
```

example:

```csv
TAR,Core,Intro to Technical Theatre,Course,1,TPA2200
TAR,Core,Intro to Tech Lab,Course,1,TPA2200L
TAR,Core,History Elective,Course,1,"THE3110,THE3111"
TAR,TAP,Performance Electives,Credits,9,"TPP3230,TPP3251C,TPP3252C,TPP3580,TPP4221,TPP4310,TPP4600,TPP4920,TPP4923"
```

definitions:
Degree            major (MTR=musical theatre, TAR=theatre)
Conc              theatre concentration (core=all, TAP=performance, TAA=theatre arts,
                  TDAT=theatre design and technology)
Requirement       requirement for degree, could be individual or group of courses
Course or Credit  whether the requirement is for a certain number of courses or credits
Quantity          number of courses or credits needed to fulfill requirement
Courses Accepted  courses that will fulfill the requirement

### 4. prerequisites.csv

stores prerequisite rules.

expected columns:

```csv
Course,'(',Requisite,Min Grade,Concurrency,')',And/Or
```

example:

```csv
THE4562,(,THE3110,C,No,,OR
THE4562,,THE3111,C,No,),AND
THE4562,(,THE4330,C,No,,OR
THE4562,,THE4401,C,No,,OR
THE4562,,THE4434,C,No,,OR
THE4562,,THE4480,C,No,)
```

definitions:
Course            course requiring prerequisites
'('               opening parenthesis for requisite groupings
Requisite         course required to take the course either as pre, or pre-co
Min Grade         minimum grade for requisite course to count
Concurrency       if requisite course must be completed prior to registration or if
                  it may be completed concurrently
')'               closing parenthesis for requisite groupings
And/Or            logic for if course must be completed in addition to or other
                  courses or as one of several options


## suggested folder structure

```text
gradpath/
│
├── data/
│   ├── theatre_majors.csv
│   ├── THE_courses.csv
│   ├── TPA_courses.csv
│   ├── TPP_courses.csv
│   ├── Practicum_courses.csv
│   ├── degree_requirements.csv
│   └── prerequisites.csv
│
├── src/
│   ├── load_data.py
│   ├── planner.py
│   ├── demand_report.py
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

## core logic

### step 1: load data

the system reads all csv files.

input files:

```text
Theatre_Majors.csv
THE_Courses.csv
TPA_Courses.csv
TPP_Courses.csv
Practicum_Courses.csv
degree_requirements.csv
prerequisites.csv
```

### step 2: clean data

the system standardizes the data before using it.

cleaning checks:

1. check for and remove duplicate rows
2. make course codes consistent
3. make concentration names consistent
4. check for missing student ids
5. check for missing course codes

example:

```text
THE3100
THE-3100
THE 3100
```

all should become:

```text
THE 3100
```

### step 3: aggrigate data

for each student, the system sorts them into separate data frames based on major and concentration. the system loads relevant columns from TheatreMajors.csv.

example:

```text
TAR-TAP df:
202608,Student3,U00000003,...,3.38,TAR,TAP

TAR-TAA df:
202608,Student2, U00000002,...,3.33,TAR,TAA

MTR df:
202608,Studet 1,U00000001,...,3.8,MTR,
```

### step 4: find required courses

the system checks the student’s concentration and columns for the requirements for that concentration.

example:

```text
theatre core:
Theatre&Culture,Entry Seminar,Script Analysis, History Elective, Hist/Theory Elective,...

theatre performace:
Acting II,Acting III,Movement for Actors,Voice for Actors,Ensemble Studio,...
```

### step 5: find completed courses

for each student, the system finds the courses they already completed.

example:

```text
U00000001 completed:
THE 2020
THE 2000
THE 3100
```

### step 5: find missing courses

the system compares completed courses with required courses.

example:

```text
completed:
THE 1000
THE 2000
THE 3100

required:
THE 1000
THE 2000
THE 3100
THE 4200

missing:
THE 4200
```

### step 6: check prerequisites

the system checks whether the student completed the prerequisites for each missing course to determine student rediness. 

example:

```text
THE 4200 requires THE 3100.
S001 completed THE 3100.
S001 is ready for THE 4200.
```

### step 7: generate intermediate data

the system outputs the intermediate data from the aggrigated spreadsheets.

example for TAR-TAP:
```csv
Term,Last Name,First Name,UID,...,USF GPA,Theatre Major,Theatre Conc,Theatre&Culture,Entry Seminar,Script Analysis,...,Acting II,Acting III,Ensemble Studio
202608,Student3,U00000003,...,3.38,TAR,TAP,c,c,ip,...,c,r,n
```

course status abbreviations:
| abbreviation    | status                |
| --------------- | --------------------- |
| c               | complete              |
| ip              | in-progress           |
| n               | incomplete/ not ready |
| r               | incomplete/ ready     |

### step 8: input intermediate data

the system inputs the intermediate data from intermediate csv files.

### step 9: estimate course need

the system analyzes several factors to determine minimum semesters until expected graduation. then, the system places each missing course into a need category.

factors considered to calculate minimum time to graduation:
1. credit hours needed to reach 120 total credits
2. class and/or admit term
3. maximum depth from capstone courses for missing courses

suggested rules:

| missing   | prereq complete | min time to     | steps away from | need category   |
| course    | or in-progress  | graduation      | course/capstone | needed in...    |
| --------- | --------------- | --------------- | --------------- | --------------- |
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


### step 8: assign priority

the system assigns a priority group to each student and course.

suggested rule:

| priority | meaning                                                          |
| -------- | ---------------------------------------------------------------- |
| high     | prereq's are complete and course is needed within 2 semesters    |
| medium   | prereq's are complete and course is needed within 3 semesters    |
| low      | prereq's are complete and course is needed in 4+ semesters       |
| none     | course is required but another course must be completed first    |

example:

```text
S001 needs THE 4200 within 1 semester.
prerequisites are complete.
priority: high

S002 needs THE 2000 within 3 semesters.
prerequisites are complete.
priority: medium

S002 needs THE 4200 wihin 2 semesters.
prerequisites are not complete.
priority: none
```

### step 9: aggregate course demand

the system counts how many students need each course in each future-semester category.

example output:

```csv
course_code,needed_1_semester,needed_2_semesters,needed_3_semesters,needed_4_plus_semesters,total_demand
THE4200,8,4,1,0,13
THE3100,5,7,2,1,15
```

### step 10: generate reports

the system exports two main reports.

#### course_demand_report.csv

shows total course demand.

expected columns:

```csv
course_code,needed_1_semester,needed_2_semesters,needed_3_semesters,needed_4_plus_semesters,total_demand
```

#### priority_students.csv

shows anonymized students who may need priority.

expected columns:

```csv
student_id,course_code,priority,reason
```

example:

```csv
S001,THE 4200,High,Prerequisites complete and course is required within 1 semester
S002,THE 4400,Medium,Prerequisites complete and course is required within 3 semesters
```

## optional streamlit dashboard later

if time allows, the group may add a simple streamlit dashboard.

the dashboard may show:

1. course demand report
2. priority student report
3. filter by course
4. filter by concentration
5. bar chart of demand by course

dashboard layout:

```text
gradpath dashboard

course demand summary
[table]

priority students
[table]

demand by course
[bar chart]
```

## development phases

### phase 1: setup

tasks:

1. create the github repository
2. create the project folders
3. create fake csv data
4. create `requirements.txt`
5. create the first version of `README.md`

goal:

the project should have a clean structure and fake data ready to use.

### phase 2: data loading

tasks:

1. read all csv files using pandas
2. print sample rows from each file
3. check that columns are loaded correctly
4. add basic error handling for missing files or missing columns

goal:

the system should successfully load all fake data.

### phase 3: requirement matching

tasks:

1. group completed courses by student
2. match each student to their concentration requirements
3. identify missing required courses

goal:

the system should know which courses each student still needs.

### phase 4: prerequisite checking

tasks:

1. read prerequisite rules
2. check whether each missing course has prerequisites
3. check whether the student completed those prerequisites
4. mark courses as eligible or blocked

goal:

the system should know whether each missing course can be taken soon.

### phase 5: course need estimation

tasks:

1. create rules for semester need categories
2. apply those rules to each student and missing course
3. label each course as needed in one, two, three, or four or more semesters

goal:

the system should estimate when each student may need each course.

### phase 6: report generation

tasks:

1. count demand by course
2. count demand by semester category
3. create priority student groups
4. export final csv reports

goal:

the system should produce useful output files.

### phase 7: optional dashboard

tasks:

1. create a streamlit app
2. display the course demand report
3. display the priority student report
4. add simple filters or charts

goal:

the project should have a simple visual demo.

## team roles

these can be adjusted later may be.

| team member        | possible role                                    |
| ------------------ | ------------------------------------------------ |
| sneha lama         | data structure, planning logic, documentation    |
| christopher pyfrom | fake data creation, requirement mapping, testing |
| joshua smith       | reports, dashboard, final presentation support   |

## minimum working version

the minimum version should include:

1. fake data files
2. python code that loads the data
3. logic that finds missing requirements
4. logic that checks prerequisites
5. logic that estimates course need categories
6. a course demand report
7. a priority student report
8. a README explaining how the project works

## later stretch features

if time allows,wecan add:

1. streamlit dashboard
2. bar chart for demand by course
3. filter by concentration
4. more fake students
5. more realistic prerequisite chains
6. simple backtesting using older fake semesters
7. summary explanation for each priority student

## risks and limits

| risk                                                | how we will handle it                                                |
| --------------------------------------------------- | -------------------------------------------------------------------- |
| fake data may not represent real students perfectly | we will clearly state that the data is fictional                     |
| course rules may be simplified                      | we will limit the project to selected theatre courses                |
| the model may not be true machine learning          | we will frame it as rule-based planning and course demand estimation |
| scope may become too large                          | we will avoid full scheduling, registration, and grade prediction    |
| requirements may vary by catalog year               | we may use one simplified requirement set for the prototype          |

## final demo plan

the final demo should show:

1. the fake data files
2. the project architecture
3. how the system loads the data
4. how missing courses are identified
5. how prerequisites are checked
6. how course need categories are assigned
7. the final course demand report
8. the priority student report
9. optional dashboard if completed

## success criteria

the project is successful if it can:

1. use student records
2. identify missing required courses
3. check prerequisites
4. estimate future course need categories
5. count demand by course
6. produce readable reports
7. explain why students are placed into priority groups

## final project summary

gradpath is a small course demand planning prototype. it uses student records, degree requirements, and prerequisites data to estimate when students may need required theatre courses. the system produces course demand counts and anonymized student priority groups to support future course planning.
