#!/usr/bin/env python3

import argparse
import re
import os
import sys
import numpy as np
import math

# =============================================================================
# Generic code
# =============================================================================

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, nargs='?', default="input.txt", help="Input file")
parser.add_argument('--verbose', '-v', action='count', default=0, help="Increase verbosity level")


args = parser.parse_args()

def _log(msg, level = 1):
    if level <= args.verbose:
        print("[DEBUG] %s" % (msg))

def print_map(map, level = 1):
    if level <= args.verbose:
        for x in range(len(map)):
            for y in range(len(map[x])):
                print(map[x][y], end="")
            print("")

def print_result(result):
    if args.verbose > 0: 
        print("\n================")
    print("Result: %s" % (result))

if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


with open(args.input_file) as f:
    raw_data = f.read().strip()

# =============================================================================
# Puzzle code
# =============================================================================

def read_data(raw_data):
    data = []
    for line in raw_data.split("\n"):
        tmp = line.split(" ")
        g = tmp[1].split(",")
        data.append({"springs": tmp[0], "groups": g})

    _log("Data:")
    for line in data:
        print("%s -> %s" % (line["springs"], ", ".join(line["groups"])))
    
    return data

def get_all_combinations(springs):
    c = []

    # Get location of all ?
    qm_list=[]
    for i in range(len(springs)):
        if springs[i] == "?":
            qm_list.append(i)

    _log("qm_list = %s" % (qm_list))
    
    for i in range(pow(2, len(qm_list))):
        tmp = [x for x in springs]
        for idx in range(len(qm_list)):
            r = "#" if i & (1 << idx) == 0 else "."
            qm_idx = qm_list[idx]
            tmp[qm_idx] = r
        c.append("".join(tmp))

    return c

def get_good_combinations(c_all, groups):

    c_good = []
    for c in c_all:
        tmp_groups = []
        num = 0
        _log("Testing combination :%s"%(c), 3)
        for x in c:
            if x == "#":
                num += 1
            elif x == "." and num > 0:
                tmp_groups.append(num)
                num = 0
        if num > 0:
            tmp_groups.append(num)
        
        if np.array_equal(np.array(tmp_groups, str), groups):
            _log("Found valid combination: %s (%s)" % (c, groups), 2)
            c_good.append(c)

    return c_good

#
# Main function
#
def get_result(raw_data):
    total = 0
    _data = read_data(raw_data)
    
    for row in _data:
        c_all = get_all_combinations(row["springs"])
        _log("Combinations for data %s:" % (row), 2)
        for c in c_all:
            _log("  %s" % (c), 2)
        

        c_good = get_good_combinations(c_all, row["groups"])
        _log("Found %s valid combination for %s" % (len(c_good), row))
        _log("Valid combinations:", 2)
        for c in c_good:
            _log("  %s" % (c), 2)

        total += len(c_good)



    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
