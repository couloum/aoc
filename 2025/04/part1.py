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

def c(text, fg=None, bg=None):
    color_map = {
        "black": 0,
        "red": 1,
        "green": 2,
        "brown": 3,
        "blue": 4,
        "purple": 5,
        "cyan": 6,
        "gray": 7,
    }

    colors=[]
    color_text = ""
    if fg:
        colors.append("3%d"%(color_map[fg]))
    if bg:
        colors.append("4%d"%(color_map[bg]))
    if len(colors) > 0:
        color_text = '\033[%sm' % (';'.join(colors))
    

    return "%s%s%s" % (color_text, text, '\033[0m')

# =============================================================================
# Puzzle code
# =============================================================================

def get_num_adj_rolls(map, y, x):
    """
    For a given point in a map, count the number of cases with a roll that are adjacent
    to that case.
    An case wit a roll is a case with symbol "@"
    """

    num_adj_rolls = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            # Do not count current position
            if dx == 0 and dy == 0:
                continue
            if not in_map(map, y+dy, x+dx):
                continue
            if map[y+dy][x+dx] == "@":
                num_adj_rolls += 1
    
    return num_adj_rolls



def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    map = read_data_map(raw_data)

    _log("Map:")
    print_map(map)

    # For each point of the map, check how many adjacent positions have a roll on it
    # Count positions with less than 4 adjacent rolls on it.
    accessibe_rolls_xy = []
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == ".":
                # Skip cases with no roll on it
                continue

            if get_num_adj_rolls(map, y, x) < 4:
                _log("Found accessible roll on position x=%d,y=%d" % (x, y))
                accessibe_rolls_xy.append(yx_to_s(y,x))
                total += 1

    # Just for debug
    if args.verbose >= 1:
        _log("List of acccessible rolls:")
        for y in range(len(map)):
            for x in range(len(map[x])):
                if yx_to_s(y,x) in accessibe_rolls_xy:
                    print('%s'%(c(map[y][x], 'red')), end="")
                else:
                    print(map[y][x], end="")
            print("")

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))