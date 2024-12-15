#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
#import numpy as np
#import math

# =============================================================================
# Generic code
# =============================================================================

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, nargs='?', default="input.txt", help="Input file")
parser.add_argument('--verbose', '-v', action='count', default=0, help="Increase verbosity level")
parser.add_argument('--interactive', '-i', action='store_true', default=False, help="Interactive mode. Force verbosity to 1")


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

def enlarge_map(map):
    new_map = []

    mapping = {
        "@": ['@', '.'],
        "O": ['[', ']'],
        "#": ['#', '#'],
        ".": ['.', '.'],
    }

    for x in range(len(map)):
        new_map.append([])
        for y in range(len(map[x])):
            new_map[x] += mapping[map[x][y]]

    return new_map

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

    return (enlarge_map(map), moves)

def apply_move(map, xy, move, level=0, mode=0):
    """
    Apply a single move (if possible) to the object location in position (x,y).
    Move objects that would prevent the move to be done.
    Return new coordonates of the object after the move
    mode define how this algorithm behaves:
    - 0 = normal behavior
    - -1 = do not apply anything
    - 1 = force movement
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

    _log("apply_move(map, %s, %s, %d, %s) '%s' -> '%s'" % (xy, move, level, mode, map[x][y], map[nx][ny]), 3)

    if map[nx][ny] == "#":
        # Impossible move
        # Return current coordonates
        _log("Return KO [%d] (%d,%d) -> (%d,%d) -> '#'" % (level, x,y,nx,ny), 3)
        return xy
    
    if map[nx][ny] in ['[', ']']:
        # If we move just left right, apply a classic move to the objects on left/right
        if move in ['<', '>']:
            # Need to apply move to the object first
            apply_move(map, xy_to_s(nx,ny), move, level+1, mode)
        
        # in case it's up/down, it's a bit more complicated, because an object can move 2 other objects
        if move in ['^', 'v']:
            nx2 = nx
            if map[nx][ny] == "[":
                ny2 = ny + 1
            else:
                ny2 = ny - 1

            # Apply moves in dry-run mode
            if  mode <= 0:
                (nnx, nny) = s_to_xy(apply_move(map, xy_to_s(nx ,ny ), move, level+1, -1))
                (nnx2, nny2) = s_to_xy(apply_move(map, xy_to_s(nx2,ny2), move, level+1, -1))
                if (nnx == nx and nny == ny) or (nnx2 == nx2 and nny2 == ny2):
                    # Impossible move
                    _log("Impossible move [%d] (%d,%d) -> (%d,%d) and (%d,%d) -> (%d,%d)" % (level, nx,ny,nnx,nny,nx2,ny2,nnx2,nny2), 3)
                    return xy
                elif mode == -1:
                    return xy_to_s(nx,ny)
            if mode >= 0:
                _log("Apply move [%d] for (%d,%d) and (%d,%d)" % (level, nx,ny,nx2,ny2),3)
                # Really apply the move if it is possible
                apply_move(map, xy_to_s(nx ,ny ), move, level+1, 1)
                apply_move(map, xy_to_s(nx2,ny2), move, level+1, 1)


    
    # Now, if we have a point to next position, we can move
    if map[nx][ny] == ".":
        # Do nothing in dry-run mode
        if mode >= 0:
            map[nx][ny] = map[x][y]
            map[x][y] = "."
        _log("Return OK [%d] (%d,%d) -> (%d,%d) -> '%s'" % (level, x,y,nx,ny, map[nx][ny]), 3)
        return xy_to_s(nx,ny)
    else:
        # Impossible move (blocked by objects that cannot move)
        _log("Return KO [%d] (%d,%d) -> (%d,%d) -> '%s'" % (level, x,y,nx,ny,map[nx][ny]), 3)
        return xy
    

def print_map_custom(map, move, failed=False):
    if failed:
        color = '\x1b[6;30;41m'
    else:
        color = '\x1b[6;30;42m'
    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == "@":
                print('%s%s\x1b[0m' % (color,move), end="")
            else:
                print(map[x][y], end="")
        print("")

def apply_moves(map, moves):
    """
    Return a new map after having applied all movement instructions to the robot
    """

    new_map = copy_map(map)

    # First identify robot coordonates
    rx = 0
    ry = 0
    for x in range(len(new_map)):
        for y in range(len(new_map[x])):
            if new_map[x][y] == "@":
                rx = x
                ry = y
                break
        if rx > 0:
            break

    _log("Robot initial position is (%d,%d)" % (rx, ry))
    # Now apply moves
    i = 1
    for move in moves:
        (new_rx,new_ry) = s_to_xy(apply_move(new_map, xy_to_s(rx,ry), move))
        not_moved = (new_rx == rx and new_ry == ry)
        (rx,ry) = (new_rx, new_ry)
        if args.interactive:
            os.system("clear")
            _log("[%d] Robot new position is (%d,%d) after move %s (%.1f %% done)" % (i, rx, ry, move, 100 * (i / len(moves))))
            print_map_custom(new_map, move, not_moved)
            time.sleep(0.1)
        i += 1
    
    _log("Robot ending position is (%d,%d)" % (rx, ry))

    return new_map

def get_sum_box_coord(map):
    """
    Calculate the coordonates (x,y) of each box ([]) from the map
    Sum these coordonates and return the result
    """

    total = 0

    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == "[":
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
if args.interactive:
    args.verbose = 1

print_result(get_result(raw_data))