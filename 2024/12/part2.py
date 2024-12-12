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

def get_nb_corners(map, x, y):
    """
    Return number of corners of a plot garden
    A corner can be define if plant type is different UP/LEFT or UP/RIGHT or DOWN/LEFT of DOWN/RIGHT.
    """
    plant_type = map[x][y]
    directions = ("-1,0:0,-1", "-1,0:0,1", "1,0:0,-1", "1,0:0,1")
    corners = 0
    for direction in directions:
        (d1, d2) = direction.split(":")

        (d1x, d1y) = s_to_xy(d1)
        (d2x, d2y) = s_to_xy(d2)

        d1_flag = False
        if x + d1x < 0 or x + d1x >= len(map) or y + d1y < 0 or y + d1y >= len(map[x]):
            d1_flag = True
        elif map[x+d1x][y+d1y] != plant_type:
            d1_flag = True
        
        d2_flag = False
        if x + d2x < 0 or x + d2x >= len(map) or y + d2y < 0 or y + d2y >= len(map[x]):
            d2_flag = True
        elif map[x+d2x][y+d2y] != plant_type:
            d2_flag = True

        if d1_flag and d2_flag:
            corners += 1
            continue

        # Now check if diagonal can be a corner
        if not d1_flag and not d2_flag:
            dx = d1x + d2x
            dy = d1y + d2y
            if x + dx < 0 or x + dx >= len(map) or y + dy < 0 or y + dy >= len(map[x]):
                continue

            if map[x+dx][y+dy] != plant_type:
                corners += 1

    return corners



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

    area = 1
    sides = 0
    corners = get_nb_corners(map, x, y)
    # 1 corner  = 2 x 0.5 side = 1 side
    # 2 corners = 1 side + 2 x 0.5 sides = 2 sides
    # 3 corners = not possible
    # 4 corners = 4 x 1 side = 4 sides

    sides += corners
    
    _log("  => %d corners found. sides=%d" % (corners, sides), 2)
    
    # Continue xploring the region
    directions = ("0,1", "1,0", "0,-1", "-1,0")
    for (dx,dy) in [s_to_xy(x) for x in directions]:
        # Don't explore outside of the map
        if x + dx < 0 or x + dx >= len(map) or y + dy < 0 or y + dy >= len(map[x]):
            continue
        # Don't explore other regions
        if map[x+dx][y+dy] != plant_type:
            continue

        (a, s) = explore_region(map, x+dx, y+dy, explored_map)
        area += a
        sides += s

    return (area, sides)
        


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
    total_sides = 0
    for x in range(len(map)):
        for y in range(len(map[x])):
            if map_explored[x][y] == ".":
                # We were already there
                continue

            # We are exploring a region that we didn't explored yet
            (area, sides) = explore_region(map, x, y, map_explored)
            _log("Region explored: plant_type=%s coord=(%d,%d) area=%d sides=%d" % (map[x][y], x, y, area, sides))
            total_area += area
            total_sides += sides
            total += area * sides

    _log("Total area = %d / total sides = %d" % (total_area, total_sides))
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))