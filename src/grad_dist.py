#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
#
#   Title:  grad_dist
#   Description:    This program runs load_data.py to create the 
#       pre_intermediate_data.csv file. Thin it convers the distance from the
#       course to the semesters needed.
#   Dependent Files:
#       - /src/
#           - load_data.py
#   Input:
#       - /data/intermediate/
#           - <prefix>pre_intermediate_data.csv
#   Output:
#       - /data/intermediate/
#           - tap_intermediate_data.csv
#           - tdat_intermediate_data.csv (future add)
#           - taa_intermediate_data.csv (future add)
#           - mtr_intermediate_data.csv (future add)
#
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #


# imports
from pathlib import Path
import os
import pandas as pd
import subprocess
import sys


####### Change This #########
debug = False


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
    print("Root: ", str(parentDir))
interDataDir = str(parentDir) + pathSep + "data" + pathSep + "intermediate" + pathSep


# files
fnIntermediateTAP = interDataDir + "tap_intermediate_data.csv"
fnPreIntermediateTAP = interDataDir + "tap_pre_intermediate_data.csv"

# get data frames
df_intermediate_tap = pd.read_csv(Path(fnPreIntermediateTAP))

# Identify relevant practicum column names
practicumCols = ['Technical Theatre Practicum I Dist', 'Lower Level Practicum Dist', 'Upper Level Practicum Dist', 'Upper Level Practicum2 Dist']

#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
#
#   Title:  get_grad_dist
#   Description:    This program calculates the number of semesters remaining.
#   Input:  singel row of data frame and index of the row
#   Output: integer for the number of semesters remaining
#
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
def get_grad_dist(df, index):
    # get base values from dataframe
    curTerm = str(df.loc[index, 'Term'])
    admitTerm = str(df.loc[index, "Admit Term"])
    usfCredits = int(df.loc[index, 'USF Earned Hours'])
    totalCredits = int(df.loc[index, 'Overall Earned Hours'])
    stuType = df.loc[index, 'Stu Type']

    # initialize variables
    maxPathLen = 0
    creditsNeeded = 0
    semNeeded = 8
    recFlag = False

    # count credits needed and identify maximum path length
    for col_name in df:
        if recFlag == False:    # skips the columns before the requirements
            if col_name == 'Theatre Conc': #last column before requirements
                recFlag = True
            continue
        else:
            if "/" in str(df.loc[index, col_name]):
                curPathDist = int(df.loc[index, col_name].split("/")[1])
                if col_name in practicumCols:   # for practicum courses
                    maxPathLen = max(maxPathLen, curPathDist)
                    creditsNeeded += 1
                elif col_name == 'Performance Electives Dist': # for performance elective
                    eleCredRemain = int(df.loc[index, col_name].split("/")[0])
                    creditsNeeded += eleCredRemain
                    # convert credits to semesters remaining
                    if eleCredRemain > 3:
                        maxPathLen = max(maxPathLen, 2) 
                    else:
                        maxPathLen = max(maxPathLen, 1)
                else:   # all other courses
                    maxPathLen = max(maxPathLen, curPathDist)
                    creditsNeeded += 3
    if debug:
        print(f"Max Path Length: {maxPathLen}")
        print(f"Credits Needed: {creditsNeeded}")

    # compare credits from missing courses to total and usf credits
    creditsNeeded = max(creditsNeeded, (120-totalCredits))
    creditsNeeded = max(creditsNeeded, (30 - usfCredits))
    # convert credits needed to semesters
    semFromCredits = ((creditsNeeded//15) if ((creditsNeeded%15) == 0) else ((creditsNeeded//15)+1))

    # calculate semesters completed at USF
    semDiff = 0
    if (curTerm[4:6] == admitTerm[4:6]):
        semDiff = 0
    elif (curTerm[4:6] == '01' and admitTerm[4:6] == '05'):
        semDiff = -1
    elif (curTerm[4:6] == '01' and admitTerm[4:6] == '08'):
        semDiff = -1
    elif (curTerm[4:6] == '08' and admitTerm[4:6] == '01'):
        semDiff = 1
    elif (curTerm[4:6] == '08' and admitTerm[4:6] == '05'):
        semDiff = 0
    else:
        semDiff = 0

    numSemesters = ((int(curTerm[0:4]) - int(admitTerm[0:4])) * 2) + semDiff + 1

    if debug:
        print(f"Max Credits Needed: {creditsNeeded}")
        print(f"Cur:{curTerm} Admit:{admitTerm} Semesters:{numSemesters}")
    # subtract semesters completed from 8 (or 4 if transfer)
    if stuType == 'B':
        semNeeded = 8 - numSemesters
    else:
        semNeeded = 4 - numSemesters
    if semNeeded < 0:
        semNeeded = 0

    if debug:
        print(f"Initial Semesters Needed: {semNeeded}")
        print(f"Semestres Needed Based on Credits: {semFromCredits}")

    # get max semesters from time at USF, credits needed, and max path
    semNeeded = max(semNeeded, semFromCredits)
    semNeeded = max(semNeeded, maxPathLen)
    semNeeded = min(semNeeded, 7) # max semesters remaining should be 7

    if debug:
        print(f"Actual Semesters Needed: {semNeeded}")

    return semNeeded
# end get_grad_dist

#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
#
#   Title:  update_crs_dist
#   Description:    This program adds the number of semesters to the distance
#       from the course.
#   Input:  number of semsters remaining, data frame, and index for the 
#       current student
#   Output: Void
#
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
def update_crs_dist(sem, df, index):
    recFlag = False

    for col_name in df:
        if recFlag == False:    # skips the columns before the requirements
            if col_name == 'Theatre Conc':
                recFlag = True
            continue
        else:
            # add semesters remaining and subtract distance from end of path
            if "/" in str(df.loc[index, col_name]):
                distToCourse = int(df.loc[index, col_name].split("/")[0])
                curPathDist = int(df.loc[index, col_name].split("/")[1])
                dist = curPathDist - distToCourse
                if debug:
                    print(f"Original: {distToCourse}/{curPathDist}")
                if col_name == 'Performance Electives Dist':
                    temp = 1 if distToCourse<=3 else 2
                    df.loc[index, col_name] = str(sem-temp) + "/" + str(distToCourse)
                else:
                    df.loc[index, col_name] = str(sem-dist) + "/" + str(curPathDist)
                if debug:
                    print(f"Converted: {df.loc[index, col_name]}")
# end update_crs_dist

#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
#
#   Title:  main
#   Description:    This program runs load_data.py to create the 
#       pre_intermediate_data.csv file. Thin it convers the distance from the
#       course to the semesters needed.
#   Dependent Files:
#       - /src/
#           - load_data.py
#   Input:
#       - /data/intermediate/
#           - <prefix>pre_intermediate_data.csv
#   Output:
#       - /data/intermediate/
#           - tap_intermediate_data.csv
#           - tdat_intermediate_data.csv (future add)
#           - taa_intermediate_data.csv (future add)
#           - mtr_intermediate_data.csv (future add)
#
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
def main():
    # build pre_intermediate_data files
    subprocess.run(["python3", "./src/load_data.py"])

    #process each student in data frame
    for ind, row in df_intermediate_tap.iterrows():
        if debug:
            if ind > 6:
                break
            print(f"\n\n\n**********{df_intermediate_tap.loc[ind, 'UID']}*********\n")
            print(row.to_frame().T)
        # calculate semesters remaining    
        grad_dist = get_grad_dist(row.to_frame().T, ind)

        # update cell values
        update_crs_dist(grad_dist, df_intermediate_tap, ind)
    
    # export to intermediate_data file
    df_intermediate_tap.to_csv(Path(fnIntermediateTAP), index=False)
    print("Intermediate Data Created Successfully!")
# end main

if __name__ == "__main__":
    main()
    