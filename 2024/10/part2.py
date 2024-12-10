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

def get_trail_paths(map, x, y, cur_path=[], valid_paths = []):
    _log("get_trail_paths(map, %d, %d, %s, %s)" % (x,y,cur_path, valid_paths), 3)

    # Add current location to the path we are exploring
    cur_path.append(xy_to_s(x,y))

    # Start with exit condition
    if map[x][y] == 9:
        # This is a valid path that we add
        _log("[OK] Found a valid trail path: %s" % (cur_path), 2)
        valid_paths.append(cur_path)
        return valid_paths
    
    # Search for valid ways => ways that are exactly 1-higher than current position
    # We only search up/down/left/right
    seek = ["-1,0", "0,1", "1,0", "0,-1"]
    possible_ways=[]
    for dxy in seek:
        (dx, dy) = s_to_xy(dxy)
        if x+dx < 0 or x+dx >= len(map) or y+dy < 0 or y+dy >= len(map[x+dx]):
            continue
        if map[x+dx][y+dy] == map[x][y] + 1:
            possible_ways.append(xy_to_s(x+dx,y+dy))
        
    # When we have identified all possible ways, explore them
    for way in possible_ways:
        (new_x, new_y) = s_to_xy(way)
        get_trail_paths(map, new_x, new_y, cur_path.copy(), valid_paths)

    return valid_paths




def get_result(raw_data):
    """
    
    """
    total = 0

    map = read_data_map(raw_data)

    # Identify coordonates of all trailheads
    trailheads = []
    for x in range(len(map)):
        for y in range(len(map[x])):
            # First convert strings into int
            map[x][y] = int(map[x][y])
            if int(map[x][y]) == 0:
                _log("Found trailhead at position (%d,%d)" % (x,y))
                trailheads.append(xy_to_s(x,y))

    _log("Found %d trailheads" % (len(trailheads)))

    trails = []
    # For each trailhead, find all paths
    for th in trailheads:
        (x,y) = s_to_xy(th)
        trails_tmp = get_trail_paths(map, x, y, [], [])
        trails += trails_tmp
        _log("Found %d trails with trailhead at coord (%d,%d)" % (len(trails_tmp),x,y))
    
    total = len(trails)

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))