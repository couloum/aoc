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
    #data = []

    return raw_data.split(",")

def get_num(puzzle, x, y):
    """
    Get value of a number at a given position
    """

    # Initialize number with digit at current position
    val = int(puzzle[x][y])

    # For each digit on the left, add this digit multiplied by index
    for i in range(y-1, -1, -1):
        char = puzzle[x][i]
        if not char.isdigit():
            break
        val += int(char) * pow(10, (y - i))

    # For each value at the right, multiply value by 10 and add value of new position
    for i in range(y+1, len(puzzle)):
        char = puzzle[x][i]
        if not char.isdigit():
            break
        val *= 10
        val += int(puzzle[x][i])

    _log("Found number %d at position (%d,%d)" % (val, x, y), 3)
    return val


def get_numbers(puzzle, x, y):
    """
    Find all numbers in a box arround a given position
    """
    numbers = []
    for i in range(-1, 2):
        for j in range (-1, 2):
            char = str(puzzle[x+i][y+j])
            if not char.isdigit():
                continue
            numbers.append(get_num(puzzle, x+i, y+j))


    # Remove all identical numbers
    numbers = list(set(numbers))

    # If only 1 number left, then add a 0 as 2nd number
    # TODO: this algorithm would not work in case the 2 numbers arround a star a guenuinly same numbers
    if len(numbers) < 2:
        numbers.append(0)

    return numbers


#
# Main function
#
def get_result(raw_data):
    total = 0
    puzzle = read_data_map(raw_data)

    # find all stars
    for x in range(len(puzzle)):
        for y in range(len(puzzle[x])):
            if puzzle[x][y] == "*":
                (a, b) = get_numbers(puzzle, x, y)
                total += a * b
                _log("Found a star on position (%d,%d) with 2 adjacent numbers: %d and %d. Total=%d" % (x, y, a, b, total))


    

    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
