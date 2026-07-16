#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
#
#   Title:  Student Data Builder
#   Author: Chris Pyfrom
#   Created:    June 30, 2026
#   Description:    This program will create sample student data sets. It will
#       produce a Student List, and Course Completion lists for each course
#       prefix and practicum courses. It will only generate courses that are
#       in-progress or passed.
#
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #


# Imports
from pathlib import Path
import os
import pandas as pd
import random

#   #   #   #   Enter Settings  #   #   #   #
debug = False
numStudents = 100
currentTerm = '202608'      # Current In-progress Semester
setType = 'Test'           # Ex: ['Train', 'Valid', 'Test']
setNum = 1
#   #   #   #   #   #   #   #   #   #   #   #


# File and Sheet names
theatreMajorsFile = f"{setType}{setNum:02}_TheatreMajors.csv"
# theatreMajorsSheet = "Majors"
theFile = f"{setType}{setNum:02}_THE_Courses.csv"
# theSheet = "THE"
tpaFile = f"{setType}{setNum:02}_TPA_Courses.csv"
# tpaSheet = "TPA"
tppFile = f"{setType}{setNum:02}_TPP_Courses.csv"
# tppSheet = "TPP"
practicumFile = f"{setType}{setNum:02}_Practicum_Courses.csv"
# practicumSheet = "Practicum"
courseListFile = "CourseList.xlsx"
courseListSheet = "CourseList"

# Get path separator based on OS
pathSep = ""
if (os.name == 'posix'):
    pathSep = "/"
else:
    pathSep = "\\"


# Get directories
currentDirPath = Path(__file__).resolve().parent
currentDir = str(currentDirPath)
if (debug):
    print("cwd: ", currentDir)

currentDir += pathSep
dataDir = str(currentDirPath.parent) + pathSep + "data" + pathSep + "raw" + pathSep

if (debug):
    print("Current Dir: ", currentDir)
    print("Data Dir: ", dataDir)


# Create Data Frames
majorsList_columns = ['Term', 'Term Description', 'Last Name', 'First Name', 'UID',
             'Count', 'Email', 'Camp', 'Coll', 'Dep 1', 'Levl', 'Prim Majr1',
             'Prim Majr2', 'Seco Majr1', 'Seco Majr2', 'Minr1', 'Minr2',
             'Prim Conc', 'Prim Conc2', 'Seco Conc', 'Seco Conc2', 'Class',
             'Admit Term', 'Enrolled [Y/N]', 'Stu Type', 'Student Type Description',
             'Student Attribute', 'USF Earned Hours', 'Overall Earned Hours',
             'USF GPA', 'Theatre Major', 'Theatre Conc']

coursesColumns = ['Prefix', 'Number', 'Course Title', 'Section', 'CRN',
               'Semester', 'UID', 'Name', 'Registration', 'Date',
               'Midterm', 'Final', 'Grade Mode', 'Credits', 
               'Final Grade Entered', 'Passing', 'Passing Override']

majorsList = []
theCourses = []
tpaCourses = []
tppCourses = []
practicum = []

courseList_df = pd.read_excel(currentDir+courseListFile, sheet_name=courseListSheet)


# Student Info Groupings
termDescription = ""
match currentTerm[4:6]:
    case '01':
        termDescription = 'Spring'
    case '05':
        termDescription = 'Summer'
    case '08':
        termDescription = 'Fall'
    case _:
        termDescription = ""
termDescription = termDescription + " " + currentTerm[0:4]

majors = ['MTR', 'TAR']
concentrations = ['TAA', 'TAP', 'TDAT']
terms = ['08', '01', '05']

letter_gpa = {
    'A+' : 4.0,     'A' : 4.0,      'A-' : 3.67,
    'B+' : 3.33,    'B' : 3.0,      'B-' : 2.67,
    'C+' : 2.33,    'C' : 2.0,      'C-' : 1.67,
    'D+' : 1.33,    'D' : 1.0,      'D-' : 0.67,
    'F' : 0
}
int_to_grade = {0:'A+', 1:'A', 2:'A-', 3:'B+', 4:'B', 5:'B-', 6: 'C+', 7:'C',
                        8:'C-', 9:'D+', 10:'D', 11:'D-', 12:'F'}

# Course Groupings
tar_coreTHEcourses = [
    ['THE2000', 'THE2023'],
    ['THE2305'],
    ['THE3110', 'THE3111'],
    ['THE3110', 'THE4264', 'THE4283', 'THE4574', 'THE3111'],
    ['THE4330', 'THE4401', 'THE4434', 'THE4480'],
    ['THE4562']
]

tar_coreTPAcourses = [
    ['TPA2200', 'TPA2200L'],
    ['TPA3007C']
]

tar_coreTPPcourses = [
    'TPP2110'
]

tar_corePracticumCourses = [
    ['TPA2290'],
    ['TPA2290', 'TPP2190'],
    ['TPA4293', 'TPP4193'],
    ['TPA4293', 'TPA4293']
]

tdat_TPAcourses = [
    'TPA3208',
    'TPA4993C',
    'TPA4298'
]

tdat_DTcourses = [
    ['TPA3289C', 'TPA4011C'],
    ['TPA3223C', 'TPA4013C'],
    ['TPA3231C', 'TPA4045C']
]

tap_Courses = [
    ['TPP3510', 'TPP3790'],
    ['TPP3155'],
    ['TPP4180'],
    ['TPP4235']
]

tap_TPPelectives = [
    'TPP3230',
    'TPP3251C',
    'TPP3252C',
    'TPP3580',
    'TPP4221',
    'TPP4310',
    'TPP4600',
    'TPP4920',
    'TPP4923'
]

taa_TPPelectives = [
    'TPP3510', 
    'TPP3790',
    'TPP3155',
    'TPP3230',
    'TPP3251C',
    'TPP3252C',
    'TPP3580',
    'TPP4221',
    'TPP4310',
    'TPP4600',
    'TPP4920',
    'TPP4923'
]

taa_TPAelectives = [
    'TPA3208',
    'TPA3289C',
    'TPA3223C',
    'TPA32231C',
    'TPA4993C'
]


#   #   #   #   Generate Students Listings  #   #   #   #
gpa_qpts = 0
gpa_credits = 0

for num in range(1, numStudents+1):

    randNum = random.randint(17, 100)
    if (debug):
        print(randNum)

    # Generate Theatre Major Info
    studentName = f"Student {num}"
    uid = "U" + str(num).zfill(8)
    maj = majors[1] if ((randNum%9) >=4) else majors[0]
    conc = None
    if maj == 'TAR':
        conc = concentrations[(randNum%5)%3]

    transfer = (randNum%11 <= 2)
    level = (randNum%4) + 1
    admitTerm = currentTerm[0:4]    # get year from current term
    admitTerm = int(admitTerm)      # convert to int
    admitTerm = admitTerm - (level-1)   # subtract level - 1 years
    admitTerm = admitTerm + (2 if (transfer and (level > 2)) else 0)    # if transfer and level>2 add 2 years
    admitTerm = str(admitTerm) + terms[(randNum%5)%3] # concat semester to end
    # admitTerm = str(int(currentTerm[0:3])-(level-1) + (2 if (transfer and (level > 2)) else 0)) + terms[(randNum//5)//3]

    semDiff = 0
    if (currentTerm[4:6] == admitTerm[4:6]):
        semDiff = 0
    elif (currentTerm[4:6] == '01' and admitTerm[4:6] == '05'):
        semDiff = -1
    elif (currentTerm[4:6] == '01' and admitTerm[4:6] == '08'):
        semDiff = -1
    elif (currentTerm[4:6] == '08' and admitTerm[4:6] == '01'):
        semDiff = 1
    elif (currentTerm[4:6] == '08' and admitTerm[4:6] == '05'):
        semDiff = 0
    else:
        semDiff = 0

    numSemesters = ((int(currentTerm[0:4]) - int(admitTerm[0:4])) * 2) + semDiff

    usf_hours = 0
    for i in range(0,numSemesters):
        usf_hours += random.randint(10,18)

    overall_hours = 0
    match (level):
        case 1:
            overall_hours = random.randint(3,12)
        case 2:
            overall_hours = random.randint(30, 59)
        case 3:
            overall_hours = random.randint(60, 89)
        case 4:
            overall_hours = random.randint(90, 119)
        case _:
            overall_hours = 0
    overall_hours = max(overall_hours, usf_hours)


    # Course helper function
    def buildCourseEntry (course, credits, gradeMode='R', ip=False, name=studentName, id=uid):
        title = courseList_df.loc[(courseList_df['Combined'] == course) & (courseList_df['Retire'].astype(int) >= int(currentTerm)) & (courseList_df['Begin'].astype(int) <= int(currentTerm)), 'Title'].item()
        grade = None
        if (gradeMode == 'R'):
            grade = None if ip else (int_to_grade[random.randint(1,100)%7])
        elif (gradeMode == 'S'):
            grade = None if ip else 'S'
        
        dataRow = {
            'Prefix':               course[0:3],     
            'Number':               course[3:],       
            'Course Title':         title,           
            'Sec':                  None, 
            'CRN':                  None, 
            'Semester':             None,
            'UID':                  id,
            'Name':                 name,  
            'Registration':         None, 
            'Date':                 None, 
            'Midterm':              None,
            'Final':                grade,
            'Grade Mode':           gradeMode,
            'Credits':              credits,
            'Final Grade Entered':  ('N' if ip else 'Y'),
            'Passing':              ('ip' if ip else 'c'),
            'Passing Override':     None 
        }
        if (debug):
            print(dataRow)

        if gradeMode == 'R' and not ip:
            global gpa_qpts
            gpa_qpts += (letter_gpa[grade] * credits)
            global gpa_credits
            gpa_credits += credits
        
        global theCourses
        global tpaCourses
        global tppCourses
        global practicum
        if (course[0:3] == 'THE'):
            theCourses.append(dataRow)
        elif (course[0:3] == 'TPA'):
            if ((course[3:] == '2290') or (course[3:] == '2292') or (course[3:] == '4293') or (course[3:] == '4298')):
                practicum.append(dataRow)
            else:
                tpaCourses.append(dataRow)
        elif (course[0:3] == 'TPP'):
            if ((course[3:] == '2190') or (course[3:] == '4193')):
                practicum.append(dataRow)
            else:
                tppCourses.append(dataRow)


    #   #   #   #   Build Theatre Courses   #   #   #   #

    #   #   All Theatre Students
    # Practicum
    for i in range(0,min(numSemesters, 4)):
        curLen = len(tar_corePracticumCourses[i])
        if numSemesters == 1:
            if ((randNum%9)%4 == 2):
                buildCourseEntry('TPP2190', 1, 'S', True)
        else:
            if i == numSemesters-1:
                match (randNum%9):
                    case 0,1:
                        pass
                    case 2,3,4:
                        buildCourseEntry(tar_corePracticumCourses[i][random.randint(0,curLen-1)], 1, 'S')
                    case _:
                        buildCourseEntry(tar_corePracticumCourses[i][random.randint(0,curLen-1)], 1, 'S', True)
            else:
                buildCourseEntry(tar_corePracticumCourses[i][random.randint(0,curLen-1)], 1, 'S')

    # TPA & TPP Core
    if (numSemesters <= 2):
        decision = (randNum%13)
        if numSemesters == 1:
            decision = (decision%3)
        match (decision):
            case 0:
                buildCourseEntry(tar_coreTPAcourses[0][0], 3, 'R', True)
                buildCourseEntry(tar_coreTPAcourses[0][1], 1, 'R', True)
                buildCourseEntry(tar_coreTPAcourses[1][0], 3, 'R', True)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3, 'R', True)
            case 1:
                buildCourseEntry(tar_coreTPAcourses[1][0], 3, 'R', True)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3, 'R', True)
            case 2:
                buildCourseEntry(tar_coreTPAcourses[0][0], 3, 'R', True)
                buildCourseEntry(tar_coreTPAcourses[0][1], 1, 'R', True)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3, 'R', True)
            case 3:
                buildCourseEntry(tar_coreTPAcourses[0][0], 3)
                buildCourseEntry(tar_coreTPAcourses[0][1], 1)
                buildCourseEntry(tar_coreTPAcourses[1][0], 3, 'R', True)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3, 'R', True)
            case 4:
                buildCourseEntry(tar_coreTPAcourses[0][0], 3, 'R', True)
                buildCourseEntry(tar_coreTPAcourses[0][1], 1, 'R', True)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPAcourses[1][0], 3)
            case 5:
                buildCourseEntry(tar_coreTPAcourses[0][0], 3)
                buildCourseEntry(tar_coreTPAcourses[0][1], 1)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3)
            case 6:
                buildCourseEntry(tar_coreTPAcourses[1][0], 3)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3, 'R', True)
            case 7:
                buildCourseEntry(tar_coreTPAcourses[0][0], 3)
                buildCourseEntry(tar_coreTPAcourses[0][1], 1)
                buildCourseEntry(tar_coreTPAcourses[1][0], 3)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3)
            case 8:
                pass
            case _:
                buildCourseEntry(tar_coreTPAcourses[0][0], 3, 'R', True)
                buildCourseEntry(tar_coreTPAcourses[0][1], 1, 'R', True)
                if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3)
    else:
        buildCourseEntry(tar_coreTPAcourses[0][0], 3)
        buildCourseEntry(tar_coreTPAcourses[0][1], 1)
        buildCourseEntry(tar_coreTPAcourses[1][0], 3)
        if (conc != 'TAP'): buildCourseEntry(tar_coreTPPcourses[0], 3)

    # Musical Theatre students only
    if (maj == 'MTR'):
        pass
    
    # Theatre students only
    if (maj == 'TAR'):
        decision = (randNum%13)
        if (numSemesters == 1):
            decision = decision%4
            match decision:
                case 0:
                    buildCourseEntry(tar_coreTHEcourses[0][0], 3)
                    buildCourseEntry(tar_coreTHEcourses[0][1], 1, 'R', True)
                case 1:
                    buildCourseEntry(tar_coreTHEcourses[0][0], 3, 'R', True)
                case _:
                    buildCourseEntry(tar_coreTHEcourses[0][0], 3, 'R', True)
                    buildCourseEntry(tar_coreTHEcourses[0][1], 1, 'R', True)
        else:
            buildCourseEntry(tar_coreTHEcourses[0][0], 3)
            buildCourseEntry(tar_coreTHEcourses[0][1], 1)
            if (numSemesters == 2):
                decision = decision%5
                match decision:
                    case 0:
                        buildCourseEntry('THE2305', 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3, 'R', True)
                    case 1:
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3, 'R', True)
                    case _:
                        buildCourseEntry('THE2305', 3, 'R', True)
            elif (numSemesters == 3):
                decision = decision%7
                match decision:
                    case 0:
                        buildCourseEntry('THE2305', 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)
                    case 1:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)
                    case 2:
                        buildCourseEntry('THE2305', 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)
                    case 3:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3, 'R', True)
                    case _:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)

            elif (numSemesters >=4 and level == 4):
                buildCourseEntry('THE2305', 3)
                buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                decision = decision%9
                match decision:
                    case 0:
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3, 'R', True)
                    case 1:
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3, 'R', True)
                        buildCourseEntry('THE4562', 3, 'R', True)
                    case 2:
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3, 'R', True)
                        buildCourseEntry('THE4562', 3, 'R', True)
                    case 3,4:
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3)
                    case 5:
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3)
                        buildCourseEntry('THE4562', 3)
                    case _:
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3)
                        buildCourseEntry('THE4562', 3, 'R', True)  
            else:
                decision = decision%7
                match decision:
                    case 0:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3, 'R', True)
                    case 1:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3)
                    case 2:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3, 'R', True)
                    case 3:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3)
                    case 4:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3, 'R', True)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3)
                    case 5:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3, 'R', True)
                    case _:
                        buildCourseEntry('THE2305', 3)
                        buildCourseEntry(tar_coreTHEcourses[2][decision%2], 3)
                        buildCourseEntry(tar_coreTHEcourses[4][decision%4], 3)
                        buildCourseEntry(tar_coreTHEcourses[3][random.randint(0,3) if (decision%2 == 1) else random.randint(1,4)], 3)

    # Theatre: Performance students only
    if (conc == 'TAP'):
        if (numSemesters == 1):
            decision = randNum%7
            match decision:
                case 0,1:
                    buildCourseEntry('TPP2110', 3)
                case 2:
                    pass
                case _:
                    buildCourseEntry('TPP2110', 3, 'R', True)
        elif (numSemesters == 2):
            decision = randNum%7
            match decision:
                case 0:
                    buildCourseEntry('TPP2110', 3, 'R', True)
                case 1:
                    buildCourseEntry('TPP2110', 3)
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                case 2:
                    buildCourseEntry('TPP2110', 3)
                    buildCourseEntry(tap_Courses[1][0], 3, 'R', True)
                case 3:
                    buildCourseEntry('TPP2110', 3)
                    buildCourseEntry(tap_Courses[0][0], 3, 'R', True)
                    buildCourseEntry(tap_Courses[1][0], 3, 'R', True)
                case 4:
                    pass
                case _:
                    buildCourseEntry('TPP2110', 3)
                    buildCourseEntry(tap_Courses[0][0], 3, 'R', True)
        elif (numSemesters == 3):
            buildCourseEntry('TPP2110', 3)
            decision = randNum%7
            match decision:
                case 0:
                    buildCourseEntry(tap_Courses[0][0], 3)
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                case 1:
                    buildCourseEntry(tap_Courses[0][0], 3)
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                    buildCourseEntry(tap_Courses[1][0], 3)
                case 2:
                    buildCourseEntry(tap_Courses[0][0], 3)
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                    buildCourseEntry(tap_Courses[1][0], 3)
                    buildCourseEntry(tap_Courses[2][0], 3, 'R', True)
                case 3:
                    buildCourseEntry(tap_Courses[0][0], 3, 'R', True)
                    buildCourseEntry(tap_Courses[1][0], 3)
                case _:
                    buildCourseEntry(tap_Courses[0][0], 3)
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                    buildCourseEntry(tap_Courses[1][0], 3, 'R', True)
        elif (numSemesters >= 4 and level == 4):
            buildCourseEntry('TPP2110', 3)
            buildCourseEntry(tap_Courses[0][0], 3)
            buildCourseEntry(tap_Courses[1][0], 3)
            decision = randNum%7
            match decision:
                case 0,1:
                    buildCourseEntry(tap_Courses[0][1], 3)
                    buildCourseEntry(tap_Courses[2][0], 3)
                case 2:
                    buildCourseEntry(tap_Courses[0][1], 3)
                    buildCourseEntry(tap_Courses[2][0], 3, 'R', True)
                case 3:
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                    buildCourseEntry(tap_Courses[2][0], 3)
                case 4:
                    buildCourseEntry(tap_Courses[0][1], 3)
                    buildCourseEntry(tap_Courses[2][0], 3)
                    buildCourseEntry(tap_Courses[3][0], 3)
                case _:
                    buildCourseEntry(tap_Courses[0][1], 3)
                    buildCourseEntry(tap_Courses[2][0], 3)
                    buildCourseEntry(tap_Courses[3][0], 3, 'R', True)
        else:
            buildCourseEntry('TPP2110', 3)
            buildCourseEntry(tap_Courses[0][0], 3)
            decision = randNum%7
            match decision:
                case 0:
                    buildCourseEntry(tap_Courses[0][1], 3)
                    buildCourseEntry(tap_Courses[1][0], 3)
                    buildCourseEntry(tap_Courses[2][0], 3)
                case 1:
                    buildCourseEntry(tap_Courses[0][1], 3)
                    buildCourseEntry(tap_Courses[1][0], 3)
                    buildCourseEntry(tap_Courses[2][0], 3)
                    buildCourseEntry(tap_Courses[3][0], 3)
                case 2:
                    buildCourseEntry(tap_Courses[0][1], 3)
                    buildCourseEntry(tap_Courses[1][0], 3)
                    buildCourseEntry(tap_Courses[2][0], 3, 'R', True)
                case 3:
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                    buildCourseEntry(tap_Courses[1][0], 3)
                    buildCourseEntry(tap_Courses[2][0], 3)
                case 4:
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                    buildCourseEntry(tap_Courses[1][0], 3)
                    buildCourseEntry(tap_Courses[2][0], 3, 'R', True)
                case 5:
                    buildCourseEntry(tap_Courses[0][1], 3, 'R', True)
                    buildCourseEntry(tap_Courses[1][0], 3)
                case _:
                    buildCourseEntry(tap_Courses[0][1], 3)
                    buildCourseEntry(tap_Courses[1][0], 3)
                    buildCourseEntry(tap_Courses[2][0], 3)
                    buildCourseEntry(tap_Courses[3][0], 3, 'R', True)
        for i in range(0,numSemesters-1):
            choice = (randNum+i)%len(tap_TPPelectives)
            if (i == numSemesters-2):
                buildCourseEntry(tap_TPPelectives[choice], 3, 'R', True)
            else:
                buildCourseEntry(tap_TPPelectives[choice], 3)


    #   #   #   #   Build Theatre Majors line entry #   #   #   #
    gpa = (None if (gpa_credits == 0) else round((gpa_qpts / gpa_credits), 2))

    majorsList.append({
        'Term':             currentTerm,
        'Term Description': termDescription,
        'Last Name':        studentName,
        'First Name':       studentName,
        'UID':              uid,
        'Count':            1,         
        'Email':            None,
        'Camp':             'T',
        'Coll':             'DP',
        'Dep 1':            'TRD',
        'Levl':             'UG',
        'Prim Majr1':       maj,
        'Prim Majr2':       None,
        'Seco Majr1':       None,
        'Seco Majr2':       None,
        'Minr1':            None,
        'Minr2':            None,
        'Prim Conc':        conc,
        'Prim Conc2':       None,
        'Seco Conc':        None,
        'Seco Conc2':       None,
        'Class':            level,
        'Admit Term':       admitTerm,
        'Enrolled [Y/N]':   'Y',
        'Stu Type':         ('J' if transfer else 'B'),
        'Student Type Description':
            ('Transfer from FL Comm. College' if transfer else 'Beginner,First time in college'), 
        
        'Student Attribute':None,
        'USF Earned Hours': usf_hours,
        'Overall Earned Hours':overall_hours,
        'USF GPA':          gpa,
        'Theatre Major':    maj,
        'Theatre Conc':     conc 
    })


#   #   #   #   Create Excel Files  #   #   #   #
majorsList_df = pd.DataFrame(majorsList, columns = majorsList_columns)
majorsList_df.to_csv(dataDir+theatreMajorsFile, index=False)

theCourses_df = pd.DataFrame(theCourses, columns=coursesColumns)
theCourses_df.to_csv(dataDir+theFile, index=False)

tpaCourses_df = pd.DataFrame(tpaCourses, columns=coursesColumns)
tpaCourses_df.to_csv(dataDir+tpaFile, index=False)

tppCourses_df = pd.DataFrame(tppCourses, columns=coursesColumns)
tppCourses_df.to_csv(dataDir+tppFile, index=False)

practicumCourses_df = pd.DataFrame(practicum, columns=coursesColumns)
practicumCourses_df.to_csv(dataDir+practicumFile, index=False)
