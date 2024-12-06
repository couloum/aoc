#!/usr/bin/env python3

import argparse
import re
import os
import sys
import numpy as np
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

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

# =============================================================================
# Puzzle code
# =============================================================================

#def read_data_custom(raw_data):
#    data = []
#    return data

#
# Main function
#
def get_result(raw_data):
    """
    
    """
    total = 0
    map = read_data_map(raw_data)

    # Identify coordonates of starting position, identified by "^"
    start_pos = (0,0)
    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == "^":
                start_pos = (x, y)
                break
    
    _log("Starting position is %s,%s" % (start_pos))

    directions = [
        (-1,0),
        (0,1),
        (1,0),
        (0,-1),
    ]
    dir_idx = 0

    # Apply algorithm from start position:
    # - Go stratight until a "#" is encountered
    # - When there's a "#" in front, turn right

    end_flag = False
    cur_pos = start_pos
    while not end_flag:
        _log("Current position: (%d,%d)" % cur_pos, 2)
        next_pos = (cur_pos[0] + directions[dir_idx][0], cur_pos[1] + directions[dir_idx][1])
        if next_pos[0] < 0 or next_pos[0] >= len(map) or next_pos[1] < 0 or next_pos[1] >= len(map):
            _log("Leaving the room at position %s,%s" % (cur_pos))
            map[cur_pos[0]][cur_pos[1]] = "X"
            end_flag = True
            continue
        
        # Turn right if we encounter a "#"
        if map[next_pos[0]][next_pos[1]] == "#":
            dir_idx = (dir_idx + 1 ) % 4
            continue
 
        # Else, go straight and mark the position
        map[cur_pos[0]][cur_pos[1]] = "X"
        cur_pos = next_pos
        
    _log("Map after guardian tour:")
    print_map(map)

    # Now count number of X in the map
    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == "X":
                total += 1

    return total
    
   

result = get_result(raw_data)
print_result(result)

        
        
