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


def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """

    # Total will be the result from the puzzle in most cases
    total = 0

    # Rotations is the list of movements from the input
    rotations = raw_data.split("\n")
    _log("Rotations: %s" % (rotations))

    # Value is the current value where the dial is pointing to
    val = 50
    for r in rotations:
        # Use a multiplier to identify if we go left or right
        multi = 1
        if r[0] == "L": # Left -> we decrese numbers
            multi = -1

        # Get the part after the first letter
        move = int(r[1:])
        
        old_val = val # Keep current value, for logging later

        # In case we're already at 0 and go left, consider that we are at 100 to avoid having a
        # negative number which would consider that we passed 0 again, while it's not true
        if val == 0 and multi == -1:
            val = 100

        # Apply the movement
        val += (move * multi)
        _log("Applying move %s. Adding %d to value %d. New value: %d" % (r, move*multi, old_val, val))

        # If new value is 0, we add 1 to the total
        if val == 0:
            total +=1
            _log("Val = 0 ! New total: %d" % (total))

        # If new value is below 0, we add 1 to the total for every time we go to 0.
        # Every time we can add 100, it means we went to 0.
        elif val < 0:
            old_val = val
            while val < 0:
                val += 100
                total += 1
            # If at the end, the value is exactly 0, we count another click on 0
            if val == 0:
                total += 1
            _log("%d < 0. New val: %d. New total: %d" % (old_val, val, total))

        # Same logic when going above 100
        elif val >= 100:
            old_val = val
            while val >= 100:
                val -= 100
                total += 1  
            _log("%d >= 100. New val: %d. New total: %d" % (old_val, val, total))  
        

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))