# GradPath Progress

## Current Stage

GradPath is currently in early implementation.

The project has moved past basic planning and documentation. The repository structure, system design, data loading, cleaning helpers, validation, and initial tests have been started. The current focus is building the intermediate data pipeline before moving into prerequisite checking and final report generation.

## Completed

* [x] created GitHub repository
* [x] added project README
* [x] added planning document
* [x] added system design document
* [x] organized project folders
* [x] added raw data folder
* [x] added intermediate data folder
* [x] added output folder
* [x] added source code folder
* [x] added tests folder
* [x] updated `.gitignore`
* [x] updated project dependencies
* [x] added cleaning utility helpers
* [x] added CSV loading logic
* [x] added CSV validation logic
* [x] added data loading tests
* [x] added course status generation
* [x] started requirement matching logic
- [x] added mock requirement status data for prerequisite and report testing
- [x] added prerequisite readiness checking
- [x] added initial final report generation
- [x] added tests for prerequisite checking and demand reports

## In Progress

* [ ] finish requirement matching dataset
* [ ] generate `data/intermediate/student_requirement_status.csv`
* [ ] test course requirement matching
* [ ] test credit requirement matching
* [ ] confirm that core and concentration requirements are applied correctly

## Next Steps

1. finish requirement matching
2. create `student_requirement_status.csv`
3. build prerequisite readiness logic
4. create `student_readiness_status.csv`
5. estimate when each missing course may be needed
6. assign student priority levels
7. generate the final course demand report
8. generate the final priority students report
9. add or update dashboard views if time allows
10. clean README and documentation before final submission

## Planned Intermediate Files

* [x] `student_course_status.csv`
* [x] `student_requirement_status.csv`
* [x] `student_readiness_status.csv`

## Planned Final Outputs

* [x] `course_demand_report.csv`
* [x] `priority_students.csv`

## Current Pipeline Status

```text
raw csv data
      |
      v
data loading and validation
      |
      v
student_course_status.csv
      |
      v
student_requirement_status.csv
      |
      v
student_readiness_status.csv
      |
      v
course demand report
      |
      v
priority students report
```

## Team Progress

### Sneha

* [x] set up the GitHub repository
* [x] created the initial README
* [x] created the initial PLANNING document
* [x] added the SYSTEM_DESIGN document
* [x] helped organize the project structure
* [x] helped define the data flow and intermediate files
* [x] worked on early implementation setup, including utilities, loading, validation, and tests

### Chris

* [x] worked on data generation
* [x] created sample student and course datasets
* [x] created degree requirement and prerequisite data files
* [x] started aggregation work for intermediate data

### Joshua

* [x] helped with documentation fixes
* [x] started report generation planning
* [ ] continue work on report generator
* [ ] support dashboard work after reports are created

## Remaining Major Work

| Task                        | Status          |
| --------------------------- | --------------- |
| Requirement matching        | in progress     |
| Prerequisite readiness      | complete        |
| Course need estimation      | not started     |
| Priority assignment         | not started     |
| Course demand report        | initial version |
| Priority students report    | initial version |
| Dashboard                   | optional later  |
| Final testing               | not started     |
| Final documentation cleanup | not started     |

## Notes

The project is still focused on the data pipeline. The dashboard should stay optional until the intermediate files and final reports are working.

The next important technical milestone is completing `student_requirement_status.csv`, because that file connects student course history to degree requirements.
