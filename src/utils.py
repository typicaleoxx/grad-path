# Begin Sneha


# end Sneha


# Begin Josh

# End Josh

# Begin Chris
import pandas as pd
import itertools
from load_data import check_complete


####### Change This #########
debug = True


prereq_list = {
    'THE4330' : [2, ['AND', 'ENG1102']],
    'THE4401' : [2, ['AND', 'ENG1102']],
    'THE4480' : [2, ['OR', 'THE3110', 'THE3111']],
    'THE4562' : [1, ['OR', 'THE3110', 'THE3111'],
                 ['OR', 'THE4330', 'THE4401', 'THE4434', 'THE4480']],
    'TPA2290' : [1, ['AND', 'TPA2200', 'TPA2200L']],
    'TPA4293' : [1, ['AND', 'TPA2200', 'TPA2290']],
    'TPP3790' : [2, ['AND', 'TPP2110']],
    'TPP3155' : [3, ['AND', 'TPP2110', 'THE2305']],
    'TPP4180' : [2, ['AND', 'TPP3155']],
    'TPP4235' : [1, ['AND', 'TPP3510', 'TPP3790', 'TPP4180']],
    'TPP3251C' : [1, ['AND', 'TPP2110']],
    'TPP3252C' : [1, ['AND', 'TPP3155', 'TPP3251C']],
    'TPP3580' : [1, ['AND', 'TPP2110']],
    'TPP4221' : [1, ['OR', 'TPP3155', 'TPP3921']],
    'TPP4310' : [1, ['AND', 'THE2305']],
    'TPP4600' : [1, ['AND', 'THE2305']],
    'TPP4920' : [1, ['OR', 'TPP3155', 'TPP3510', 'TPP3790']],
    'TPP4923' : [1, ['AND', 'TPP2110']]
}


def check_prereqs(uid, course):
    max_dist = 1
    chklst = prereq_list[course]
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
                    min_dist = 1
                    for crs in req_list[1:]:
                        stat = check_complete(uid, [crs])
                        if (stat == 'c') or (stat == 'ip'):
                            or_flag = True
                            break
                        else:
                            stat = check_prereqs(uid, crs)
                            min_dist = min(min_dist, stat[2]+1)
                    if or_flag == False:
                        and_flag = False
                    max_dist = max(max_dist, min_dist)
                elif req_list[0] == 'AND':
                    for crs in req_list[1:]:
                        stat = check_complete(uid, [crs])
                        if (stat == 'c') or (stat == 'ip'):
                            pass
                        else:
                            and_flag = False
                            stat = check_prereqs(uid, crs)
                            max_dist = max(max_dist, stat[2]+1)
        depth = depth + (max_dist-1)
        if and_flag:
            return ('r', 1, depth)
        else:
            return ('n', max_dist, depth)



def check_readiness(uid, courses, requirement, df_curRow) :
    min_dist = 1
    min_depth = 99
    for course in courses:
        status = check_prereqs(uid, course)
        min_dist = min(min_dist, status[1])
        min_depth = min(min_depth, status[2])
    if min_dist == 1:
        return ('r', min_dist, min_depth)
    else:
        return ('n', min_dist, min_depth)





# End Chris