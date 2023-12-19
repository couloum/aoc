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

    tmp = []
    for line in raw_data.split("\n"):
        if len(line) > 0:
            tmp.append([x for x in line])
        else:
            data.append(tmp)
            tmp = []
    
    data.append(tmp)

    return data

#
# Main function
#
def get_result(raw_data):
    total = 0
    _data = read_data(raw_data)
    
    idx = 0
    for puzzle in _data:
        
        _log("Processing puzzle #%d:" % (idx))

        for x in puzzle:
            _log("  %s" % (x))


        # Find horizontal or vertical symetries
        for j in range(2):
            factor = 100 if j == 0 else 1
            way = "vertical" if j == 0 else "horizontal"
            _log("Checking puzzle on %s axis (factor=%d)" % (way, factor))

            # Use a sliding window to check symetries
            # x x x x x x x
            # .|.               i=0, w_min1=0, w_max1=1, w_min2=1, w_max2=2, w_size=1
            # . .|. .           i=1, w_min1=0, w_max1=2, w_min2=2, w_max2=4, w_size=2 
            # . . .|. . .       i=2, w_min1=0, w_max1=3, w_min2=3, w_max2=6, w_size=3
            #   . . .|. . .     i=3, w_min1=1, w_max1=4, w_min2=4, w_max2=7, w_size=3
            #       . .|. .     i=4, w_min1=3, w_max1=5, w_min2=5, w_max2=7, w_size=2
            #           .|.     i=5, w_min1=5, w_max1=6, w_min2=6, w_max2=7, w_size=1

            # We always check symetries verticaly (per rows).
            # After 1 check, we rotate the puzzle so we check horizontal simetry still using rows.
            for i in range(0, len(puzzle)-1):
                p_middle = len(puzzle) / 2
                # Compute window size, min and max
                w_size = math.floor((p_middle - abs(p_middle - i - 1)))
                w_min1 = max(0, i - (w_size - 1))
                w_max1 = w_min1 + w_size
                w_min2 = w_max1
                w_max2 = min(w_min2 + w_size, len(puzzle))
                # Create 2 arrays that we will compare. Flip the 2nd array to remove the symetry
                tmp1 = np.array(puzzle[w_min1:w_max1])
                tmp2 = np.flipud(puzzle[w_min2:w_max2])

                if np.array_equal(tmp1, tmp2):
                    # If arrays are equal, it means they were symetricals
                    score = (i+1)*factor
                    total += score
                    _log("Found a symetry at index %d! Adding score %d. New total=%d" % (i, score, total))

            
            puzzle = np.swapaxes(puzzle, 1, 0) # Rotate the puzzle for next check

        idx += 1

    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
