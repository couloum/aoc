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

def is_valid_pid(id):
    """
    Return True id product IDs is valid. False otherwise.
    A product ID is invalid if if it is made only of some sequence of digits
    repeated at least twice. So, 12341234 (1234 two times), 123123123 (123
    three times), 1212121212 (12 five times), and 1111111 (1 seven times) are
    all invalid IDs.
    """

    # Convert id in string and get its length
    s_id = f"{id}"
    l = len(s_id)
    l2 = int(l/2)

    _log("Evaluating pid %d" % (id), 2)

    # Check all possibilities of lengths where a repetition is possible
    # From half the size (divide in 2 parts)
    # to 1 (divide in as many part as there are digits)
    for slice in range(1, l2+1):
        # Do not check this slice if we cannot divide number in equal parts
        if l % slice > 0:
            continue

        a = s_id[0:slice]
        pos = slice
        valid_flag = False
        #_log("Slice is %d. Reference is %s" % (slice, a), 3)
        while not valid_flag and pos + slice <= l:
            end = pos + slice
            b = s_id[pos:end]
            # If there is no repetition, the produt ID is valid
            #_log("Comparing %s with %s" % (a, b), 3)
            if a != b:
                #_log("No repetition found so far. Trying with another slice", 3)
                valid_flag = True
                continue
            pos += slice
        if not valid_flag:
            #_log("Repetition found. This is an invalid pid", 3)
            # We found a repetition! mark the product ID as invalid
            return False

    #_log("No repetition found at all. This is a valid pid", 2)
    # If we are here, we did not find a repetition. Therefore, product ID is valid
    return True

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
           if not is_valid_pid(i):
                invalid_pids += 1
                total += i
                _log("Found an invalid product ID: %s. #invalid pids=%d. New total=%d" % (i, invalid_pids, total))

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))