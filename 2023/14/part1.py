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

    return data


def tilt(puzzle):
    # First, we rotate the puzzle by -90° as it is simpler to deal with lines
    # than with columns

    puzzle = np.rot90(puzzle, k=1, axes=(0,1))

    _log("Map after rot90:", 2)
    print_map(puzzle, 2)

    # Then, move to the left all "0" as much as possible
    for line in puzzle:
        free_idx = -1
        for idx in range(len(line)):
            item = line[idx]
            if item == ".":
                # Search for next O and move it to this position
                for j in range(idx+1, len(line)):
                    item2 = line[j]
                    if item2 == "#":
                        break
                    if item2 == "O":
                        line[idx] = "O"
                        line[j] = "."
                        break
            
    _log("Map after tilt:", 2)
    print_map(puzzle, 2)
    
    # Then rotate again by 90°

    puzzle = np.rot90(puzzle, k=1, axes=(1,0))
                        
            

    return puzzle

#
# Main function
#
def get_result(raw_data):
    total = 0
    _puzzle = read_data_map(raw_data)

    _log("Map before:")
    print_map(_puzzle)

    _puzzle = tilt(_puzzle)

    _log("Map after:")
    print_map(_puzzle)

    # Now count score
    for idx in range(len(_puzzle)):
        score = len(_puzzle) - idx
        for item in _puzzle[idx]:
            if item == "O":
                _log("Adding %d with rock" % (score))
                total += score

    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
