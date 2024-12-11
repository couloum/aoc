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

# def read_data_custom(raw_data):
#    data = []
#    return data

def get_nb_stones(digit, blinks):

    _log("get_nb_stones(%d,%d)" % (digit, blinks), 3)
    if blinks == 0:
        return 1
    
    if digit == 0:
        total = get_nb_stones(1, blinks - 1)
    elif len(str(digit)) % 2 == 0:
        half = int(len(str(digit)) / 2)
        digit1 = int(str(digit)[0:half])
        digit2 = int(str(digit)[half:])
        total = get_nb_stones(digit1, blinks - 1)
        total += get_nb_stones(digit2, blinks - 1)
    else:
        total = get_nb_stones(digit * 2024, blinks - 1)
    
    return total




def get_result(raw_data):
    """
    
    """
    total = 0

    data = [int(x) for x in raw_data.split(" ")]

    for digit in data:
        _log("Calculating with digit %d" % (digit))
        total += get_nb_stones(digit, 25)
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))