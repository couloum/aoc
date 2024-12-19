#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
import numpy as np
#import math

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

def xy_to_s(x, y):
    return "%d,%d" % (x,y)

def s_to_xy(xy):
    (x, y) = xy.split(",")
    return (int(x), int(y))

def in_map(map, x, y):
    """
    Tell if a given location is inside (True) or outside (False) of a given map (2D array)
    """
    if x < 0 or x >= len(map):
        return False
    if y < 0 or y >= len(map[x]):
        return False
    return True

def copy_map(map):
    """
    Create a copy of a map
    """
    new_map = []
    for x in range(len(map)):
        new_map.append(map[x].copy())
    return new_map

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

# =============================================================================
# Puzzle code
# =============================================================================

def read_data_custom(raw_data):
    lines = raw_data.split("\n")
    towels = [x.strip() for x in lines[0].split(",")]
    lines.pop(0)
    lines.pop(0)
    designs = lines

    return (towels, designs)
    
def check_design(towels, design):
    """
    Recursive function to check if we can match a design with the given towels.
    We try to match the longest pattern possible (maximum size of all towels)
    If possible, we recursively match the rest of the design
    If not possible, we reduce by 1 the size of the pattern we want to match
    """

    if len(design) == 0:
        return True
    
    # Get maximum pattern size
    max_size = max([len(x) for x in towels])
                   
    for i in range(max_size, 0, - 1 ):
        pattern = design[0:i]
        _log("Looking for a towel matching pattern %s" % (pattern), 2)
        if pattern in towels:
            _log("Pattern %s found in design %s" % (pattern, design), 2)
            if check_design(towels, design[i:]):
                return True
    
    return False


def get_result(raw_data):
    """
    
    """
    total = 0

    (towels, designs) = read_data_custom(raw_data)
    
    _log("Available towels: %s" % (towels))
    _log("Designs to create: %s" % (designs))

    for design in designs:
        _log("Checking design %s" % (design), 2)
        if check_design(towels, design):
            _log("[OK] Possible to create design %s" % (design))
            total += 1
        else:
            _log("[!!] Impossible to create design %s" % (design))

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))