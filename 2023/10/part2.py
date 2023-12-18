#!/usr/bin/env python3

import argparse
import re
import os
import sys

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

def print_map(map):
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

# =============================================================================
# Puzzle code
# =============================================================================

def read_data(raw_data):
    data = []
    for line in raw_data.split("\n"):
        data.append([x for x in line])

    _log("Data:")
    print_map(data)
    
    return data

def find_start(_map):
    for x in range(len(_map)):
        for y in range(len(_map[x])):
            if _map[x][y] == "S":
                return (x,y)


def find_starting_pipe(_map, start_pos):
    """
    Find which pipe should be present instead of S
    """
    valid_pipes = {
        (-1, 0): ['|', '7', 'F'], #Above pipes must go to south
        (0, -1): ['-', 'L', 'F'], #Left pipes must got to west
        (0, 1):  ['-', 'J', '7'], #Right pipes must got to east
        (1, 0):  ['|', 'L', 'J'], #Bottom pipes must go to north
    }
    valid_neighbors = []
    for xy in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
        x = xy[0]
        y = xy[1]
        pipe = _map[start_pos[0] + x][start_pos[1] + y]
        if pipe in valid_pipes[xy]:
            _log("Pipe '%s' on %s is valid" % (pipe, xy))
            key = str(x)+str(y)
            valid_neighbors.append(key)

    valid_neighbors.sort()
    key=str(valid_neighbors[0])+str(valid_neighbors[1])

    _log("Valid neighbors: %s (key=%s)" % (valid_neighbors, key))
    starting_pipe_map = {
        "-100-1": 'J',
        "-1001": 'L',
        "-1010": '|',
        "0-101": '-',
        "0-110": '7',
        "0110": 'F'
    }

    return starting_pipe_map[key]
    #return 'F'

next_dir_map = {
    '-': [(0, -1), (0, 1)],
    '|': [(-1, 0), (1, 0)],
    '7': [(0, -1), (1, 0)],
    'L': [(-1, 0), (0, 1)],
    'J': [(-1, 0), (0, -1)],
    'F': [(0, 1), (1, 0)]
}

def get_next_pos(_map, cur_pos, prev_pos):
    # Get pipe of current position
    cur_pipe = _map[cur_pos[0]][cur_pos[1]]

    # Get the 2 possible ways to move from current posititon
    next_directions = next_dir_map[cur_pipe]

    next_positions = [ (cur_pos[0] + x[0], cur_pos[1] + x[1]) for x in next_directions]

    # Remove position from prev_pos
    try:
        _log("Next positions: %s" % (next_positions), 3)
        next_positions.remove(prev_pos)
        _log("Removed posititon (%s, %s)" % (prev_pos), 3)
    except ValueError:
        pass

    return next_positions[0]

def is_not_enclosed(_map, pos, _map_meta):

    (x, y) = pos

    # Check Above
    for x2 in range(1, len(_map)):
        test_x = x - x2
        # If test_x < 0, just stop
        if test_x < 0:
            break
        # If we hit a wall, just stop
        if _map_meta[test_x][y] == "W":
            break
        # If we hit a point considered as not enclosed, return True
        if _map_meta[test_x][y] == "O":
            _log("Point in position (%d, %d) touches not enclosed point in positition (%d, %d)" % (x, y, test_x, y), 3)
            return True
        
    # Check left
    for y2 in range(1, len(_map[0])):
        test_y = y - y2
        # If test_y < 0, just stop
        if test_y < 0:
            break
        # If we hit a wall, just stop
        if _map_meta[x][test_y] == "W":
            break
        # If we hit a point considered as not enclosed, return True
        if _map_meta[x][test_y] == "O":
            _log("Point in position (%d, %d) touches not enclosed point in positition (%d, %d)" % (x, y, x, test_y), 3)
            return True
        
    # Check right
    for y2 in range(1, len(_map[0])):
        test_y = y + y2
        # If test_y > max_y, just stop
        if test_y >= len(_map[0]):
            break
        # If we hit a wall, just stop
        if _map_meta[x][test_y] == "W":
            break
        # If we hit a point considered as not enclosed, return True
        if _map_meta[x][test_y] == "O":
            _log("Point in position (%d, %d) touches not enclosed point in positition (%d, %d)" % (x, y, x, test_y), 3)
            return True
        
    
    # Check below
    for x2 in range(1, len(_map)):
        test_x = x + x2
        # If test_x > max_x, just stop
        if test_x >= len(_map):
            break
        # If we hit a wall, just stop
        if _map_meta[test_x][y] == "W":
            break
        # If we hit a point considered as not enclosed, return True
        if _map_meta[test_x][y] == "O":
            _log("Point in position (%d, %d) touches not enclosed point in positition (%d, %d)" % (x, y, test_x, y), 3)
            return True

        
    # If we're here, we did not touch any existig not enclosed point.
    _log("Point in position (%d, %d) does not touch any not enclosed point" % (x, y), 3)
    return False

def enlarge_map(_map):
    """
    Convert each single point of the map into a 3x3 square.
    Each pipe is extended, like this:
         ...
    F -> .F-
         .|.
         .|.
    J -> -J.
         ...

    This way, pipes that are close to each other become separated:
            .|..|.
            .|..|.
    ||   => .|..|.
    |L   => .|..|.
            .|..L-
            .|....
    """

    pipes_map = {
        '|': [ [y for y in x] for x in ".|.;.|.;.|.".split(";") ],
        '-': [ [y for y in x] for x in "...;---;...".split(";") ],
        'F': [ [y for y in x] for x in "...;.F-;.|.".split(";") ],
        'J': [ [y for y in x] for x in ".|.;-J.;...".split(";") ],
        '7': [ [y for y in x] for x in "...;-7.;.|.".split(";") ],
        'L': [ [y for y in x] for x in ".|.;.L-;...".split(";") ],
        '.': [ [y for y in x] for x in "...;xxx;...".split(";") ], # Set 3 "x" here for not enclosed points calculation
    }

    max_x = len(_map)
    max_y = len(_map[0])

    # Create enlarged map, 3 times larger and 3 times higher
    enlarged_map = [ ["." for y in range(3*max_y)] for x in range(3*max_x)]

    for x in range(max_x):
        for y in range(max_y):
            pipe = _map[x][y]
            for i in range(3):
                for j in range(3):
                    enlarged_map[3*x+i][3*y+j] = pipes_map[pipe][i][j]

    return enlarged_map

def part2(raw_data):
    total = 0
    _map = read_data(raw_data)
    
    start_pos = find_start(_map)
    
    _log("Starting point is at position (%s, %s)" % (start_pos))

    starting_pipe = find_starting_pipe(_map, start_pos)
    _log("Starting pipe is actually: %s" % (starting_pipe))
    _map[start_pos[0]][start_pos[1]] = starting_pipe

    _map = enlarge_map(_map)
    print_map(_map)

    start_pos = ( start_pos[0] * 3 + 1, start_pos[1] * 3 + 1 )

    max_x=len(_map)
    max_y=len(_map[0])

    # Create a map with metadata:
    # W = wall
    # O = not enclosed point
    # . = any other point (status unknown)

    _map_meta = [ [ "." for y in range(max_y)] for x in range(max_x)]

    cur_pos = start_pos
    last_pos = cur_pos
    nb_steps = 0
    while True:
        # Set current point as a Wall as we are going on the looping pipe.
        _map_meta[cur_pos[0]][cur_pos[1]] = "W"
        next_pos = get_next_pos(_map, cur_pos, last_pos)
        next_pipe = _map[next_pos[0]][next_pos[1]]
        _log("Next pipe is %s at position %s" % (next_pipe, next_pos), 2)
        if next_pos == start_pos:
            _log("We have returned to starting position after %d steps. Ending now" %(nb_steps))
            break

        nb_steps += 1
        last_pos = cur_pos
        cur_pos = next_pos

    _log("")
    _log("="*80)
    _log("Starting part 2")
    _log("="*80)
    _log("")

    # Update metadata map with list of points which are not enclosed.
    # By default, all positions which are at the border of the map are not
    # enclosed. Don't overwrite metadata about walls
    for i in range(max_x):
        if _map_meta[i][0] == ".":
            _map_meta[i][0] = "O"
        if _map_meta[i][max_y-1] == ".":
            _map_meta[i][max_y-1] = "O"  

    for i in range(1, max_y - 1):
        if _map_meta[0][i] == ".":
            _map_meta[0][i] = "O"
        if _map_meta[max_x-1][i] == ".":
            _map_meta[max_x-1][i] = "O"  


    # Now, for each point of the map, identify if in the same line or same column
    # we can reach a position wich is part of not_enclosed_list
    nb_update = 1
    nb_loop = 1
    while nb_update > 0:
        nb_update = 0
        for x in range(max_x):
            for y in range(max_y):
                if _map_meta[x][y] != ".":
                    # If the point is already a wall or a not enclosed point, skip it
                    continue
                if is_not_enclosed(_map, (x, y), _map_meta):
                    # This point is considered as not enclosed. Add it to the list
                    _map_meta[x][y] = "O"
                    nb_update += 1
        
        _log("After %d loop, found %d points touching a not enclosed one" % (nb_loop, nb_update))
        nb_loop += 1
    
    #Print map with only walls and enclosed items
    total = 0
    for x in range(max_x):
        for y in range(max_y):
            if _map_meta[x][y] == "W":
                # W = walls. Print the pipe
                print("%s" % (_map[x][y]), end="")
            elif _map_meta[x][y] == "O":
                # O = not enclosed point. Print a space
                print(" ", end="")
            elif _map[x][y] != ".":
                # Everything else that is not a point on the map should be considered as an enclosed point.
                # Represent it with a small x.
                # We add one to the total of not enclosed points
                total += 1
                print("x", end="")
            else:
                print(_map[x][y], end="")
        print("")

    # As we enlarged the map by a factor of 3, we must divide total found by 3.
    # That's why we replace a single point (.) with a triple x (xxx). So we count a single point as 3 small x.
    total /= 3

    return int(total)


result = part2(raw_data)
print_result(result)

        
        
