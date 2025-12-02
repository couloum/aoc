#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
import math

# =============================================================================
# Generic code
# =============================================================================

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, nargs='?', default="input.txt", help="Input file")
parser.add_argument('--verbose', '-v', action='count', default=0, help="Increase verbosity level")
parser.add_argument('--interactive', '-i', action='store_true', default=False, help="Run in interactive mode")


args = parser.parse_args()
if args.interactive:
    args.verbose = 0

def _log(msg, level = 1):
    if level <= args.verbose:
        print("[DEBUG] %s" % (msg))

def print_map(map, level = 1):
    output = ""
    if level <= args.verbose:
        for y in range(len(map)):
            for x in range(len(map[y])):
                output += map[y][x]
            output += "\n"
        print(output)

def print_result(result):
    if args.verbose > 0: 
        print("\n================")
    print("Result: %s" % (result))

if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


with open(args.input_file) as f:
    raw_data = f.read().strip()

def yx_to_s(y, x):
    return "%d,%d" % (y,x)

def s_to_yx(yx):
    (y, x) = yx.split(",")
    return (int(y), int(x))

def in_map(map, y, x):
    """
    Tell if a given location is inside (True) or outside (False) of a given map (2D array)
    """
    if y < 0 or y >= len(map):
        return False
    if x < 0 or x >= len(map[y]):
        return False
    return True

def copy_map(map):
    """
    Create a copy of a map
    """
    new_map = []
    for y in range(len(map)):
        new_map.append(map[y].copy())
    return new_map

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

# =============================================================================
# Puzzle code
# =============================================================================

def get_pid_ranges(raw_data):
    """
    From a single string with ranges of product ids, like that:
    11-22,95-115,998-1012,1188511880-1188511890,222220-222224
    Return an array of product ids, with this structure:
    {'start': 11, 'end': 22}
    """
    result = []
    for i in raw_data.split(','):
        (start, end) = i.split('-')
        result.append({'start': int(start), 'end': int(end)})
    return result

def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """

    # Total will be the result from the puzzle in most cases
    total = 0
    # Count the number of invalid product ids for stat
    invalid_pids = 0

    ranges = get_pid_ranges(raw_data)

    _log("List of ranges: %s" % (ranges))
    
    for r in ranges:
        start = r['start']
        end = r['end']

        _log("Evaluating range from %d to %d" % (start, end))
        for i in range(start, end+1):
            # Convert number in string and get its length
            si = f"{i}"
            l = len(si)

            # Number with odd number of digits are excluded
            if l % 2 == 1 :
                continue

            # Get half of the length of the number
            l2 = int(l/2)

            # Check if 1st half is equal to 2nd half
            if si[0:l2] == si[l2:]:
                total += i
                invalid_pids += 1
                _log("Found an invalid product ID: %s. #invalid pids=%d. New total=%d" % (si, invalid_pids, total))

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))