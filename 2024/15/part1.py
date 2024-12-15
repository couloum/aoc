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

def read_data_custom(raw_data):
    map = []
    moves = ""

    for line in raw_data.split("\n"):
        if len(line) < 1:
            continue
        if line[0] == "#":
           map.append([x for x in line])
        elif line[0] in ['^', '<', '>', 'v']:
          moves += line 

    return (map, moves)

def apply_move(map, xy, move):
    """
    Apply a single move (if possible) to the object location in position (x,y).
    Move objects that would prevent the move to be done.
    Return new coordonates of the object after the move
    """

    move_dict = {
        "^": "-1,0",
        "v": "1,0",
        "<": "0,-1",
        ">": "0,1",
    }

    (x,y) = s_to_xy(xy)
    (dx,dy) = s_to_xy(move_dict[move])
    (nx,ny) = (x+dx,y+dy)

    if map[nx][ny] == "#":
        # Impossible move
        # Return current coordonates
        return xy
    
    if map[nx][ny] == "O":
        # Need to apply move to the object first
        apply_move(map, xy_to_s(nx,ny), move)
    
    # Now, if we have a point to next position, we can move
    if map[nx][ny] == ".":
        map[nx][ny] = map[x][y]
        map[x][y] = "."
        return xy_to_s(nx,ny)
    else:
        # Impossible move (blocked by objects that cannot move)
        return xy


def apply_moves(map, moves):
    """
    Return a new map after having applied all movement instructions to the robot
    """

    new_map = copy_map(map)

    # First identify robot coordonates
    rx = 0
    ry = 0
    for x in range(len(new_map)):
        for y in range(len(new_map)):
            if new_map[x][y] == "@":
                rx = x
                ry = y
                break
        if rx > 0:
            break

    _log("Robot initial position is (%d,%d)" % (rx, ry))
    # Now apply moves
    for move in moves:
        (rx,ry) = s_to_xy(apply_move(new_map, xy_to_s(rx,ry), move))
    
    _log("Robot ending position is (%d,%d)" % (rx, ry))

    return new_map

def get_sum_box_coord(map):
    """
    Calculate the coordonates (x,y) of each box (O) from the map
    Sum these coordonates and return the result
    """

    total = 0

    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == "O":
                total += 100 * x + y

    return total


def get_result(raw_data):
    """
    
    """
    total = 0

    (map, moves) = read_data_custom(raw_data)

    
    print_map(map)

    if args.verbose > 0:
        _log("Moves:")
        for i in range(len(moves)):
            print(moves[i], end="")
            if i % 80 == 79:
                print("")
        print("")
    
    new_map = apply_moves(map, moves)

    _log("Map after all moves:")
    print_map(new_map)

    total = get_sum_box_coord(new_map)

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))