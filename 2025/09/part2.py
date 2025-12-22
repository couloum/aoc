#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
import math
from collections import defaultdict
from shapely.geometry import Polygon, box
from shapely.prepared import prep

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
        print(_c("\n================", "yellow"))
    print(_c("Result: %s" % (result), "yellow", bold=True))

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

def _c(text, fg=None, bg=None, bold=False, italic=False, dark=False, underline=False, reverse=False, strike=False):
    color_map = {
        "black": 0,
        "gray": 0,
        "grey": 0,
        "red": 1,
        "green": 2,
        "brown": 3,
        "yellow": 3,
        "blue": 4,
        "purple": 5,
        "cyan": 6,
        "white": 7,
    }

    colors=[]
    color_text = ""
    if bold:
      colors.append("1")
    if dark:
      colors.append("2")
    if italic:
      colors.append("3")
    if underline:
      colors.append("4")
    if reverse:
      colors.append("7")
    if reverse:
      colors.append("9")
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

def is_inside(t1: tuple, t2: tuple, poly):
    rect = box(min(t1[0], t2[0]), min(t1[1], t2[1]),
               max(t1[0], t2[0]), max(t1[1], t2[1]))

    if poly.covers(rect):
        return True
    
    return False

def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    tiles_xy = [tuple(map(int, x.split(","))) for x in raw_data.split("\n")]

    # I must admit that I used chatGPT for this one...
    poly = Polygon(tiles_xy)
    prepared = prep(poly)

    
    max_area = 0
    cur_tile = 0
    for t1 in tiles_xy:
        for t2 in tiles_xy[cur_tile+1:]:
            if is_inside(t1, t2, prepared):
                _log("Rectangle formed by %s<->%s is inside the walls" % (t1, t2))
                area = (abs(t2[0] - t1[0]) + 1 ) * (abs(t2[1] - t1[1]) + 1)
                if area > max_area:
                    _log("New max area of %d with tiles (%d,%d) and (%d,%d)" % (area, t1[0], t1[1], t2[0], t2[1]))
                    max_area = area
        cur_tile += 1

    total = max_area
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))