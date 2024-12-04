#!/usr/bin/env python3

import argparse
import re
import os
import sys
import numpy as np
#import math

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

#def read_data_custom(raw_data):
#    data = []
#    return data

def is_xmas(grid, x, y):
    """
    identify if we see "MAS" written 2 times in diagonal at this position,
    where "A" letter is at the position.
    There are 4 possible combinations:
    M-M  M-S  S-M  S-S
    -A-  -A-  -A-  -A-
    S-S  M-S  S-M  M-M
    """

    diag1 = False
    diag2 = False

    # Search in diaginal1 (from left/up to right/down)
    if (grid[x-1][y-1] == "M" and grid[x+1][y+1] == "S") or (grid[x-1][y-1] == "S" and grid[x+1][y+1] == "M"):
        diag1 = True

    # Search in diaginal2 (from right/up to left/down)
    if (grid[x-1][y+1] == "M" and grid[x+1][y-1] == "S") or (grid[x-1][y+1] == "S" and grid[x+1][y-1] == "M"):
        diag2 = True

    return diag1 and diag2

#
# Main function
#
def get_result(raw_data):
    """
    Iterate over all letters of the grid and search for "A" which are central in every X-MAS combinations.
    When a A is found, check if we have diagonal "MAS" written 2 times
    """

    total = 0
    grid = read_data_map(raw_data)

    _log("Initial grid:")
    print_map(grid)

    # Start at 1 and end 1 before length of array, because "A" letter that we search for
    # is always at 1 letter from the border
    for x in range(1, len(grid) - 1):
        for y in range(1, len(grid) - 1):
            if grid[x][y] == "A":
                _log("Evaluating sub-grid on position (%d,%d)" %(x, y))
                if is_xmas(grid, x, y):
                    _log("[OK] sub-grid is matching X-MAS pattern!")
                    total += 1


    return total
    
   

result = get_result(raw_data)
print_result(result)

        
        
