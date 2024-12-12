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

def explore_region(map, x, y, explored_map):
    """
    Explore a region: try to find all plant of same type in the neighbourhood.
    When done, compute area (number of garden plots) and perimeter
    """

    # Do not explore a plot already explored
    if explored_map[x][y] == ".":
        return (0,0)
    
    # Now this plot has been explored
    explored_map[x][y] = "."
    
    plant_type = map[x][y]

    directions = ("0,1", "1,0", "0,-1", "-1,0")

    area = 1
    perimeter = 0
    for (dx,dy) in [s_to_xy(x) for x in directions]:
        # Add a fence if we are at the border of the map
        if x + dx < 0 or x + dx >= len(map) or y + dy < 0 or y + dy >= len(map[x]):
            perimeter += 1
            continue
        # Add a fence if neighboor plant type is different
        if map[x+dx][y+dy] != plant_type:
            perimeter += 1
            continue
        # if same plant type, explore the region from here
        (a, p) = explore_region(map, x+dx, y+dy, explored_map)
        area += a
        perimeter += p

    return (area, perimeter)
        


def get_result(raw_data):
    """
    Get area and permimeter of all regions containing same plants in all garden plots
    Each garden plot contain a single type of flower (1 letter)
    Condition to have a fence:
    - A garden plot is at the border of the map
    - A garden plot is next to another plot of a different type
    """
    total = 0

    map = read_data_map(raw_data)
    map_explored = [ x.copy() for x in map ]

    total_area = 0
    total_perimeter = 0
    for x in range(len(map)):
        for y in range(len(map[x])):
            if map_explored[x][y] == ".":
                # We were already there
                continue

            # We are exploring a region that we didn't explored yet
            (area, perimeter) = explore_region(map, x, y, map_explored)
            _log("Region explored: plant_type=%s coord=(%d,%d) area=%s perimeter=%s" % (map[x][y], x, y, area, perimeter))
            total_area += area
            total_perimeter += perimeter
            total += area * perimeter

    _log("Total area = %d / total perimeter = %d" % (total_area, total_perimeter))
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))