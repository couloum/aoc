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

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

# =============================================================================
# Puzzle code
# =============================================================================

def read_data_custom(raw_data):
    data = []
    for line in raw_data.split("\n"):
        data.append([int(x) for x in line.split(" ")])

    return data

#
# Main function
#
def get_result(raw_data):
    total = 0
    data = read_data_custom(raw_data)

    for report in data:
        # If 1st number is > last number, reverse the array so we can always check
        # if serie is increasing
        if report[0] > report[-1]:
            report.reverse()

        _log("Report: %s" % (report), 2)
        valid = True
        for i in range(len(report) - 1):
            # Check that number after current is increased by at most 3
            if not (report[i+1] > report[i] and report[i+1] < report[i] + 4):
                _log("[!!] Report %s is invalid" % (report))
                valid = False
        
        if valid:
            total += 1
            _log("[OK] Report %s is valid" % (report))
    

    return int(total)


result = get_result(raw_data)
print_result(result)

        
        