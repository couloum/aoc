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

def resolve_map(map, start_pos):
    """
    Simply apply all the rules for the guard to a given map
    Return True if there's an exit and False otherwise
    """
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
    seen_count = 0
    max_seen = 200

    while not end_flag:
        _log("Current position: (%d,%d)" % cur_pos, 2)
        next_pos = (cur_pos[0] + directions[dir_idx][0], cur_pos[1] + directions[dir_idx][1])

        # If next position is end of maze, leave
        if next_pos[0] < 0 or next_pos[0] >= len(map) or next_pos[1] < 0 or next_pos[1] >= len(map):
            end_flag = True
            map[cur_pos[0]][cur_pos[1]] = "X"
            continue

        # Turn right if we encounter a "#" and don't move
        if map[next_pos[0]][next_pos[1]] == "#":
            dir_idx = (dir_idx + 1 ) % 4
            continue

        # Check if current position is one we already visited befoire going on
        # If it's an unvisited place, then reset counter of visited places
        if map[cur_pos[0]][cur_pos[1]] == "X":
            seen_count += 1
        elif map[cur_pos[0]][cur_pos[1]] == ".":
            seen_count = 0

        # If we passed already "max_seen" times on a position aleady see, we consider that we're in
        # an infinite loop
        if seen_count >= max_seen:
            _log("Infinite loop detected", 2)
            end_flag = True
 
        # Go straight and mark the position
        map[cur_pos[0]][cur_pos[1]] = "X"
        cur_pos = next_pos

    _log("Leaving the room at position %s,%s" % (cur_pos), 2)

    return seen_count < max_seen

def is_infinite_map(map, start_pos):
    """
    Return the opposite boolean of resolve_map (ie, map cannot be resolved)
    """

    return not resolve_map(map, start_pos)

def get_path_coord(map, start_pos):
    """
    Provide in an array all coordonates where the guard walked on.
    """

    test_map = np.array(map)
    # First resolve the map
    resolve_map(test_map, start_pos)

    # Then, get coordonate of all locations where there's a X
    coord = []
    for x in range(len(test_map)):
        for y in range(len(test_map[x])):
            if test_map[x][y] == "X":
                coord.append((x,y))

    return coord

#
# Main function
#
def get_result(raw_data):
    """
    Brute force algorithm:
    Try adding a "#" in every location where there's a '.' and check if the map become a dead end
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

    # Get coordonates of all places where the guard walk when map is untouched
    for coord in get_path_coord(map, start_pos):
            x = coord[0]
            y = coord[1]

            # Add an obstacle at current position and check if map become a dead-end
            # First, copy the original map because the function to test "dead-end" situation is destructive
            test_map = np.array(map)
            test_map[x][y] = "#"

            if is_infinite_map(test_map, start_pos):
                total += 1
                _log("[OK] map become infinite by adding an obstacle on position (%d,%d). total=%d" % (x, y, total))
            else:
                _log("[!!] map is not infinite by adding an obstacle on position (%d,%d). total=%d" % (x, y, total))
   
        


    return total
    
   

result = get_result(raw_data)
print_result(result)

        
        
