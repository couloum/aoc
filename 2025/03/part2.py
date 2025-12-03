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

def get_highest_num(string):
    """
    From a string containing digits only, get the value and position of first highest digit
    """

    _log("Searching larget digit in string %s" % (string), 3)
    max_num = -1
    max_num_pos = -1
    for i in range(9, 0, -1):
        try:
            max_num_pos = string.index(f"{i}")
            max_num = i
            break
        except ValueError:
            continue
        
    return (max_num, max_num_pos)


def get_max_joltage(bank):
    """
    From a power bank, get the association of 12 batteries that create the maximum joltage.
    The batteries are arranged into banks; each line of digits in your input corresponds
    to a single bank of batteries. Within each bank, you need to turn on exactly twelve
    batteries; the joltage that the bank produces is equal to the number formed by the
    digits on the batteries you've turned on.
    For example, In 987654321111111, the largest joltage can be found by turning on
    everything except some 1s at the end to produce 987654321111.
    """

    # We will iterate 12 times over the power bank to find largest number from all batteries.
    # Each time, we exclude the last batteries:
    # - At 1st iteration, we exclude the last 11 digits
    # - At 2nd iteration, we exclude the last 10 digits
    # ...
    # - At the last iteration, we don't exclude any digit
    #
    # Each time, we start parsing from the position of previous largest number.
    #
    # Example with power bank '234234234234278'.
    # We search highest number in string '2342' (full power bank, excluding the last 11 batteries) => 4
    # We can now start searching after the 4 and exclude the last 10 batteries.
    # We search in highest number in string '23' => 3
    # We continue by searching in string '4234234278', but exclude the last 9 digits, so search only in '4' => 4
    # We continue up to excluding no entry

    joltage = ""
    cur_pos = 0
    for i in range(12, 0, -1):
        # Get the maximum number for a battery (excluding batteries that are out of range)
        out_limit=i-1
        if out_limit > 0:
            string = bank[cur_pos:-out_limit]
        else:
            # bank[cur_pos:-0] does not exist. We have to manage it differently
            string = bank[cur_pos:]
        
        #_log("cur_pos=%d out_limit=-%d" % (cur_pos, out_limit),3)
        # Get highest number from the string in which we search
        (max_num, max_num_pos) = get_highest_num(string)
        cur_pos += max_num_pos + 1
        _log("[%d] Maximum number for battery is %s at index %d" % (i, max_num, cur_pos - 1), 2)
        joltage = "%s%s" % (joltage, max_num)

    return int(joltage)


def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    # Get all power banks
    banks = raw_data.split("\n")

    i = 1
    for bank in banks:
        _log("Evaluating power bank #%d" % (i))
        _log("Power bank value: %s" % (bank), 3)
        # For each power bank get max number
        joltage = get_max_joltage(bank)
        total += joltage
        _log("Max joltage is %d. total=%d" % (joltage, total))
        i += 1  

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))