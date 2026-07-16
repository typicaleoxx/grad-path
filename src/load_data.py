# Begin Sneha


# end Sneha


# Begin Josh

# End Josh

# Begin Chris

# imports
from pathlib import Path
import os
import pandas as pd
import itertools
from utils import prereq_list


####### Change This #########
debug = False
filePrefix = "Train01_"

def check_pre_complete (id, accCrsList):
    pass

def check_complete (id, accCrsList):
    pass

def check_prereqs(uid, course):
    max_dist = 1
    chklst = prereq_list.get(course)
    if chklst == None:
        return ('r', 1, 1)
    else:
        depth = 0
        and_flag = True
        for ind, req_list in enumerate(chklst):
            if ind == 0:
                depth = req_list
            else:
                if req_list[0] == 'OR':
                    or_flag = False
                    min_dist = 999
                    for crs in req_list[1:]:
                        stat = check_pre_complete(uid, [crs])
                        if (stat == 'c') or (stat == 'ip'):
                            or_flag = True
                            min_dist = 1
                            break
                        else:
                            stat = check_prereqs(uid, crs)
                            min_dist = min(min_dist, stat[1]+1)
                    if or_flag == False:
                        and_flag = False
                    max_dist = max(max_dist, min_dist)
                elif req_list[0] == 'AND':
                    for crs in req_list[1:]:
                        stat = check_pre_complete(uid, [crs])
                        if (stat == 'c') or (stat == 'ip'):
                            pass
                        else:
                            and_flag = False
                            stat = check_prereqs(uid, crs)
                            max_dist = max(max_dist, stat[1]+1)
                            if debug:
                                print("MaxDist:", max_dist)
        depth = depth + (max_dist-1)
        if debug:
            print("MaxDist:", max_dist, " Depth:", depth)
            print("Ready:", and_flag)
        if and_flag:
            return ('r', 1, depth)
        else:
            return ('n', max_dist, depth)



def check_readiness(uid, courses) :
    min_dist = 99
    min_depth = 99
    for course in courses:
        status = check_prereqs(uid, course)
        min_dist = min(min_dist, status[1])
        min_depth = min(min_depth, status[2])
    if min_dist == 1:
        return ('r', min_dist, min_depth)
    else:
        return ('n', min_dist, min_depth)
    # pass



# Get path separator based on OS
pathSep = ""
if (os.name == 'posix'):
    pathSep = "/"
else:
    pathSep = "\\"


# Directories
currentDir = Path(__file__).resolve().parent
if debug:
    print("cwd: ", str(currentDir))
parentDir = currentDir.parent
if debug:
    print("Parent Dir: ", str(parentDir))
rawDataDir = str(parentDir) + pathSep + "data" + pathSep + "raw" + pathSep
staticDataDir = str(parentDir) + pathSep + "data" + pathSep + "static" + pathSep
interDataDir = str(parentDir) + pathSep + "data" + pathSep + "intermediate" + pathSep


#files
fnMajors = rawDataDir + filePrefix + "TheatreMajors.csv"
fnTHE = rawDataDir + filePrefix + "THE_Courses.csv"
fnTPA = rawDataDir + filePrefix + "TPA_Courses.csv"
fnTPP = rawDataDir + filePrefix + "TPP_Courses.csv"
fnPracticum = rawDataDir + filePrefix + "Practicum_Courses.csv"
fnPrereqs = staticDataDir + "prerequisites.csv"
fnDegreeReq = staticDataDir + "degree_requirements.csv"
fnIntermediateTAP = interDataDir + "tap_intermediate_data.csv"

#get data frames
majorCols = ['Term', 'Last Name', 'First Name', 'UID', 'Class', 'Admit Term', 
             'Stu Type', 'USF Earned Hours','Overall Earned Hours', 'USF GPA',
             'Theatre Major', 'Theatre Conc']
courseCols = ['Prefix', 'Number', 'Course Title', 'UID', 'Name', 'Final',
                 'Grade Mode', 'Credits', 'Passing']
df_Majors = pd.read_csv(Path(fnMajors), usecols= majorCols)
df_THE_Courses = pd.read_csv(Path(fnTHE), usecols=courseCols)
df_THE_Courses['Full Course'] = df_THE_Courses['Prefix'] + df_THE_Courses['Number'].astype('string')
df_THE_Courses['Used'] = None
df_TPA_Courses = pd.read_csv(Path(fnTPA), usecols=courseCols)
df_TPA_Courses['Full Course'] = df_TPA_Courses['Prefix'] + df_TPA_Courses['Number'].astype('string')
df_TPA_Courses['Used'] = None
df_TPP_Courses = pd.read_csv(Path(fnTPP), usecols=courseCols)
df_TPP_Courses['Full Course'] = df_TPP_Courses['Prefix'] + df_TPP_Courses['Number'].astype('string')
df_TPP_Courses['Used'] = None
df_Practicum_Courses = pd.read_csv(Path(fnPracticum), usecols=courseCols)
df_Practicum_Courses['Full Course'] = df_Practicum_Courses['Prefix'] + df_Practicum_Courses['Number'].astype('string')
df_Practicum_Courses['Used'] = None
df_Prereqs = pd.read_csv(Path(fnPrereqs))
df_DegreeReqs = pd.read_csv(Path(fnDegreeReq))


#get degree requirements
coreReqs = []
tapReqs = []
tdatReqs = []
taaReqs = []

for index, row in df_DegreeReqs.iterrows():
    conc = row['Conc']
    coc = row['Course or Credit']
    qn = row['Quantity']
    if (conc == 'Core'):
        coreReqs.append(row['Requirement'])
        coreReqs.append((row['Requirement']) + " Dist")
        if (coc == 'Course'):
            for i in range(2,(int(qn)+1),1):
                coreReqs.append((row['Requirement']) + str(i))
                coreReqs.append((row['Requirement']) + str(i) + " Dist")
    elif (conc == 'TAP'):
        tapReqs.append(row['Requirement'])
        tapReqs.append((row['Requirement']) + " Dist")
        if (coc == 'Course'):
            for i in range(2,(qn+1),1):
                tapReqs.append((row['Requirement']) + str(i))
                tapReqs.append((row['Requirement']) + str(i) + " Dist")
    elif (conc == 'TDAT'):
        tdatReqs.append(row['Requirement'])
        tdatReqs.append((row['Requirement']) + " Dist")
        if (coc == 'Course'):
            for i in range(2,(qn+1),1):
                tdatReqs.append((row['Requirement']) + str(i))
                tdatReqs.append((row['Requirement']) + str(i) + " Dist")
    elif (conc == 'TAA'):
        taaReqs.append(row['Requirement'])
        taaReqs.append((row['Requirement']) + " Dist")
        if (coc == 'Course'):
            for i in range(2,(qn+1),1):
                taaReqs.append((row['Requirement']) + str(i))
                taaReqs.append((row['Requirement']) + str(i) + " Dist")


#setup intermediate file
tapIntermediateCols = list(itertools.chain(coreReqs, tapReqs))
tdatIntermediateCols = list(itertools.chain(majorCols, coreReqs, tdatReqs))
taaIntermediateCols = list(itertools.chain(majorCols, coreReqs, taaReqs))
tapIntermediateData = []
tdatIntermediateData = []
taaIntermediateData = []


for index, row in df_Majors.iterrows():
    maj = row['Theatre Major']
    conc = row['Theatre Conc']
    if (maj == 'TAR'):
        if (conc == 'TAP'):
            tapIntermediateData.append(row.tolist())
        elif (conc == 'TDAT'):
            tdatIntermediateData.append(row.tolist())
        elif (conc == 'TAA'):
            taaIntermediateData.append(row.tolist())

if debug:
    print(tdatIntermediateData)

def check_pre_complete (id, accCrsList):
    condition = ((df_THE_Courses['Full Course'].isin(accCrsList)) &
                                  (df_THE_Courses['UID'] == id) &
                                  (df_THE_Courses['Used'] == 'y'))
    complete = df_THE_Courses.loc[condition]
    if len(complete) > 0:
        firstIndex = df_THE_Courses[condition].index[0]
        if debug:
            print(complete)
            print(df_THE_Courses.loc[firstIndex, 'Full Course'])
            print(df_THE_Courses.loc[firstIndex, 'Passing'])
        return df_THE_Courses.loc[firstIndex, 'Passing']
    else:
        condition = ((df_TPA_Courses['Full Course'].isin(accCrsList)) &
                                  (df_TPA_Courses['UID'] == id) &
                                  (df_TPA_Courses['Used'] == 'y'))
        complete = df_TPA_Courses.loc[condition]
        if len(complete) > 0:
            firstIndex = df_TPA_Courses[condition].index[0]
            if debug:
                print(complete)
                print(df_TPA_Courses.loc[firstIndex, 'Full Course'])
                print(df_TPA_Courses.loc[firstIndex, 'Passing'])
            return df_TPA_Courses.loc[firstIndex, 'Passing']
        else:
            condition = ((df_TPP_Courses['Full Course'].isin(accCrsList)) &
                                  (df_TPP_Courses['UID'] == id) &
                                  (df_TPP_Courses['Used'] == 'y'))
            complete = df_TPP_Courses.loc[condition]
            if len(complete) > 0:
                firstIndex = df_TPP_Courses[condition].index[0]
                if debug:
                    print(complete)
                    print(df_TPP_Courses.loc[firstIndex, 'Full Course'])
                    print(df_TPP_Courses.loc[firstIndex, 'Passing'])
                return df_TPP_Courses.loc[firstIndex, 'Passing']
            else:
                condition = ((df_Practicum_Courses['Full Course'].isin(accCrsList)) &
                                  (df_Practicum_Courses['UID'] == id) &
                                  (df_Practicum_Courses['Used'] == 'y'))
                complete = df_Practicum_Courses.loc[condition]
                if len(complete) > 0:
                    firstIndex = df_Practicum_Courses[condition].index[0]
                    if debug:
                        print(complete)
                        print(df_Practicum_Courses.loc[firstIndex, 'Full Course'])
                        print(df_Practicum_Courses.loc[firstIndex, 'Passing'])
                    return df_Practicum_Courses.loc[firstIndex, 'Passing']
                else:
                    return None


def check_complete (id, accCrsList):
    condition = ((df_THE_Courses['Full Course'].isin(accCrsList)) &
                                  (df_THE_Courses['UID'] == id) &
                                  (df_THE_Courses['Used'] != 'y'))
    complete = df_THE_Courses.loc[condition]
    if len(complete) > 0:
        firstIndex = df_THE_Courses[condition].index[0]
        df_THE_Courses.loc[firstIndex, 'Used'] = 'y'
        if debug:
            print(complete)
            print(df_THE_Courses.loc[firstIndex, 'Full Course'])
            print(df_THE_Courses.loc[firstIndex, 'Passing'])
        return df_THE_Courses.loc[firstIndex, 'Passing']
    else:
        condition = ((df_TPA_Courses['Full Course'].isin(accCrsList)) &
                                  (df_TPA_Courses['UID'] == id) &
                                  (df_TPA_Courses['Used'] != 'y'))
        complete = df_TPA_Courses.loc[condition]
        if len(complete) > 0:
            firstIndex = df_TPA_Courses[condition].index[0]
            df_TPA_Courses.loc[firstIndex, 'Used'] = 'y'
            if debug:
                print(complete)
                print(df_TPA_Courses.loc[firstIndex, 'Full Course'])
                print(df_TPA_Courses.loc[firstIndex, 'Passing'])
            return df_TPA_Courses.loc[firstIndex, 'Passing']
        else:
            condition = ((df_TPP_Courses['Full Course'].isin(accCrsList)) &
                                  (df_TPP_Courses['UID'] == id) &
                                  (df_TPP_Courses['Used'] != 'y'))
            complete = df_TPP_Courses.loc[condition]
            if len(complete) > 0:
                firstIndex = df_TPP_Courses[condition].index[0]
                df_TPP_Courses.loc[firstIndex, 'Used'] = 'y'
                if debug:
                    print(complete)
                    print(df_TPP_Courses.loc[firstIndex, 'Full Course'])
                    print(df_TPP_Courses.loc[firstIndex, 'Passing'])
                return df_TPP_Courses.loc[firstIndex, 'Passing']
            else:
                condition = ((df_Practicum_Courses['Full Course'].isin(accCrsList)) &
                                  (df_Practicum_Courses['UID'] == id) &
                                  (df_Practicum_Courses['Used'] != 'y'))
                complete = df_Practicum_Courses.loc[condition]
                if len(complete) > 0:
                    firstIndex = df_Practicum_Courses[condition].index[0]
                    df_Practicum_Courses.loc[firstIndex, 'Used'] = 'y'
                    if debug:
                        print(complete)
                        print(df_Practicum_Courses.loc[firstIndex, 'Full Course'])
                        print(df_Practicum_Courses.loc[firstIndex, 'Passing'])
                    return df_Practicum_Courses.loc[firstIndex, 'Passing']
                else:
                    return None
                
def check_num_complete (id, accCrsList, req):
    reqCredits = df_DegreeReqs.loc[df_DegreeReqs['Requirement'] == req, 'Quantity' ].values[0]
    creditsNeeded = reqCredits
    ip_flag = False
    condition = ((df_THE_Courses['Full Course'].isin(accCrsList)) &
                                  (df_THE_Courses['UID'] == id) &
                                  (df_THE_Courses['Used'] != 'y'))
    complete = df_THE_Courses.loc[condition]
    for index in range(0, len(complete), 1):
        if creditsNeeded > 0:
            itemIndex = df_THE_Courses[condition].index[index]
            itemCredits = df_THE_Courses.loc[itemIndex, 'Credits']
            creditsNeeded -= itemCredits
            if (df_THE_Courses.loc[itemIndex, 'Passing'] == 'ip'):
                ip_flag = True
            df_THE_Courses.loc[itemIndex, 'Used'] = 'y'
        else:
            break
    if creditsNeeded > 0:
        condition = ((df_TPA_Courses['Full Course'].isin(accCrsList)) &
                                  (df_TPA_Courses['UID'] == id) &
                                  (df_TPA_Courses['Used'] != 'y'))
        complete = df_TPA_Courses.loc[condition]
        for index in range(0, len(complete), 1):
            if creditsNeeded > 0:
                itemIndex = df_TPA_Courses[condition].index[index]
                itemCredits = df_TPA_Courses.loc[itemIndex, 'Credits']
                creditsNeeded -= itemCredits
                if (df_TPA_Courses.loc[itemIndex, 'Passing'] == 'ip'):
                    ip_flag = True
                df_TPA_Courses.loc[itemIndex, 'Used'] = 'y'
            else:
                break
    if creditsNeeded > 0:
        condition = ((df_TPP_Courses['Full Course'].isin(accCrsList)) &
                                  (df_TPP_Courses['UID'] == id) &
                                  (df_TPP_Courses['Used'] != 'y'))
        complete = df_TPP_Courses.loc[condition]
        for index in range(0, len(complete), 1):
            if creditsNeeded > 0:
                itemIndex = df_TPP_Courses[condition].index[index]
                itemCredits = df_TPP_Courses.loc[itemIndex, 'Credits']
                creditsNeeded -= itemCredits
                if (df_TPP_Courses.loc[itemIndex, 'Passing'] == 'ip'):
                    ip_flag = True
                df_TPP_Courses.loc[itemIndex, 'Used'] = 'y'
            else:
                break
    if creditsNeeded > 0:
        condition = ((df_Practicum_Courses['Full Course'].isin(accCrsList)) &
                                  (df_Practicum_Courses['UID'] == id) &
                                  (df_Practicum_Courses['Used'] != 'y'))
        complete = df_Practicum_Courses.loc[condition]
        for index in range(0, len(complete), 1):
            if creditsNeeded > 0:
                itemIndex = df_Practicum_Courses[condition].index[index]
                itemCredits = df_Practicum_Courses.loc[itemIndex, 'Credits']
                creditsNeeded -= itemCredits
                if (df_Practicum_Courses.loc[itemIndex, 'Passing'] == 'ip'):
                    ip_flag = True
                df_Practicum_Courses.loc[itemIndex, 'Used'] = 'y'
            else:
                break
    status = None
    if creditsNeeded == 0:
        status = ('c', 0, 0)
    else:
        if (ip_flag):
            status = ('ip', creditsNeeded, reqCredits)
        else:
            status = ('n', creditsNeeded, reqCredits)
    return status
    
def check_Practicum(id):
    accCrsList = ['TPA2290', 'TPP2190', 'TPA4293', 'TPP4193']
    condition = ((df_Practicum_Courses['Full Course'].isin(accCrsList)) &
                                  (df_Practicum_Courses['UID'] == id) &
                                  (df_Practicum_Courses['Used'] != 'y'))
    complete = df_Practicum_Courses.loc[condition]
    pracNeeded = 4 - len(complete)
    if (pracNeeded > 0):
        return pracNeeded
    else:
        return 0



##### BUILD TAP DATA FRAME #####
df_tapIntermediate = pd.DataFrame(tapIntermediateData, columns=majorCols)
for col in tapIntermediateCols:
    df_tapIntermediate[col] = None

for index, row in df_tapIntermediate.iterrows():
    if debug and index >6:
        break
    curUID = row['UID']
    if debug:
        print("\n\n\n*************", curUID, "************\n")

    curDist = 0
    pracNeeded = 4
    for col in coreReqs:
        if not (col.endswith("Dist")):
            acceptCourses = (df_DegreeReqs.loc[df_DegreeReqs['Requirement'] == (col[:-1] if (col[-1]).isnumeric() else col), 'Courses Accepted'].values[0]).split(",")
            if debug:
                print("Req:" + col + " Courses:" + str(acceptCourses))
            if (col == 'Technical Theatre Practicum I' or col == 'Lower Level Practicum' or col == 'Upper Level Practicum' or col == 'Upper Level Practicum2'):
                if (col == 'Technical Theatre Practicum I'):
                    pracNeeded = check_Practicum(curUID)
                status = check_complete(curUID, acceptCourses)
                if (status != None):
                    df_tapIntermediate.loc[index, col] = status
                    curDist = 0
                else:
                    status = check_readiness(curUID, acceptCourses) 
                    curDist = str(status[1]) + "/" + str(pracNeeded)
                    df_tapIntermediate.loc[index, col] = status[0]
            else:
                status = check_complete(curUID, acceptCourses)
                if (status != None):
                    df_tapIntermediate.loc[index, col] = status
                    curDist = 0
                else:
                    status = check_readiness(curUID, acceptCourses) 
                    curDist = str(status[1]) + "/" + str(status[2])
                    df_tapIntermediate.loc[index, col] = status[0]
        else:
            df_tapIntermediate.loc[index, col] = curDist
    for col in tapReqs:
        if not (col.endswith("Dist")):
            acceptCourses = (df_DegreeReqs.loc[df_DegreeReqs['Requirement'] == col, 'Courses Accepted'].values[0]).split(",")
            if debug:
                print("Req:" + col + " Courses:" + str(acceptCourses))
            if col == 'Performance Electives':
                status = check_num_complete(curUID, acceptCourses, col)
                if status[0] == 'c':
                    curDist = 0
                else:
                    curDist = str(status[1]) + "/" + str(status[2])
                df_tapIntermediate.loc[index, col] = status[0]
            else:
                status = check_complete(curUID, acceptCourses)
                if (status != None):
                    df_tapIntermediate.loc[index, col] = status
                    curDist = 0
                else:
                    status = check_readiness(curUID, acceptCourses) 
                    curDist = str(status[1]) + "/" + str(status[2])
                    df_tapIntermediate.loc[index, col] = status[0]
        else:
            df_tapIntermediate.loc[index, col] = curDist


            
df_tapIntermediate.to_csv(fnIntermediateTAP, index=False)
print("Intermediate Data File...Process Complete!")

# End Chris