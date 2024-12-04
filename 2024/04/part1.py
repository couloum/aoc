#!/usr/bin/env python3

import argparse
import re
import os
import sys
#import numpy as np
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

def grid_into_strings(grid):
    """
    Transform a grid of letter (grid must be square) into an array of strings
    We have to read the grid horizontally, vertically and in diagonal to get all strings.
    """

    strings = []

    # Get horizontal and vertical strings
    for x in range(len(grid)):
        horiz = ""
        vert = ""
        for y in range(len(grid)):
            horiz += grid[x][y]
            vert += grid[y][x]
        
        strings.append(horiz)
        strings.append(vert)


    grid_size = len(grid)
    # Get diagonal strings. We need at least 4 letters per string, so ignore diagonals where there is less
    for xy in range(grid_size):
        xy2 = (grid_size - 1) - xy

        # This is the starting point.
        diag1 = ""
        diag2 = ""
        diag3 = ""
        diag4 = ""

        for inc in range(grid_size - xy):

            # Read diagonal \
            # Start from 0,0 and read when x move (diag1) or when y move (diag2)
            if (xy + inc < grid_size):
                diag1 += grid[inc][xy+inc]
                diag2 += grid[xy+inc][inc]
        
            _log("xy=%d xy2=%d inc=%d" % (xy, xy2, inc), 3)
            # Read diagonal /
            if (xy + inc < grid_size):
                diag3 += grid[xy2-inc][inc]
                diag4 += grid[(grid_size - 1) - inc][xy+inc]

        # Keep only strings where there are at least 4 letters
        if len(diag1) >= 4:
            _log("Append string diag1: %s" % (diag1), 2)
            strings.append(diag1)
        if xy > 0 and len(diag2) >= 4:
            _log("Append string diag2: %s" % (diag2), 2)
            strings.append(diag2)
        
        if len(diag3) >= 4:
            _log("Append string diag3: %s" % (diag3), 2)
            strings.append(diag3)

        if xy2 < (grid_size - 1) and len(diag4) >= 4:
            _log("Append string diag4: %s" % (diag4), 2)
            strings.append(diag4)

    return strings

#
# Main function
#
def get_result(raw_data):
    """
    For this puzzle, we must find and count all occurences of XMAS in a square grid containing letters.
    Word XMAS can be writen horizontally, verically, and in diagonal both / and \\). And the word can be read backward.

    My solution:
    Transform the grid into an array of strings, where each item of the array is one line of the grid.
    We have to read the grid horizontally, vertically and in diagonal to get all strings.
    Then, in each string we will search for words XMAS and SAMX
    """
    total = 0
    grid = read_data_map(raw_data)

    strings = grid_into_strings(grid)

    _log("List of strings: \n%s" % (str.join("\n", strings)))

    for string in strings:
        res = re.findall("(XMAS)", string)
        flag = False
        if res:
            _log("[OK] Found pattern XMAS  %d times in string %s" % (len(res), string))
            total += len(res)
            flag = True
        res = re.findall("(SAMX)", string)
        if res:
            _log("[OK] Found pattern SAMX  %d times in string %s" % (len(res), string))
            total += len(res)
            flag = True
        
        if not flag:
            _log("[!!] No pattern found in string %s" % (string))

    return total
    
   

result = get_result(raw_data)
print_result(result)

        
        
