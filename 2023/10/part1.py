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

def part1(raw_data):
    total = 0
    _map = read_data(raw_data)
    
    start_pos = find_start(_map)
    
    _log("Starting point is at position (%s, %s)" % (start_pos))

    starting_pipe = find_starting_pipe(_map, start_pos)
    _log("Starting pipe is actually: %s" % (starting_pipe))
    _map[start_pos[0]][start_pos[1]] = starting_pipe

    cur_pos = start_pos
    last_pos = cur_pos
    nb_steps = 0
    while True:
        next_pos = get_next_pos(_map, cur_pos, last_pos)
        next_pipe = _map[next_pos[0]][next_pos[1]]
        _log("Next pipe is %s at position %s" % (next_pipe, next_pos))
        if next_pos == start_pos:
            _log("We have returned to starting position after %d steps. Ending now" %(nb_steps))
            break

        nb_steps += 1
        last_pos = cur_pos
        cur_pos = next_pos
    
    total = int((nb_steps / 2) + 0.5)
    
    return total


result = part1(raw_data)
print_result(result)

        
        
