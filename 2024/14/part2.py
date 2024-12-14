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
   data = []
   regexp = re.compile(r'p=([0-9]+,[0-9]+) v=(-?[0-9]+,-?[0-9]+)')

   for line in raw_data.split("\n"):
       _log("line='%s'" % (line), 3)
       match = regexp.fullmatch(line)
       data.append({'p': match.group(1), 'v': match.group(2)})

   return data
 
def print_robots_on_map(positions, map_size):
    (map_size_x, map_size_y) = s_to_xy(map_size)

    for y in range(map_size_y):
        for x in range(map_size_x):
            nb = positions.count("%s,%s" % (x,y))
            if nb > 9:
                print("+", end="")
            elif nb > 0:
                print(nb, end="")
            else:
                print(".", end="")
        print("")


def get_position_after(start_pos, velocity, map_size, iterations):
    """
    Calculate the position of robot after a given number of iterations, considering:
    - robot velocity (movement per iteration)
    - map size
    """

    (start_pos_x, start_pos_y) = s_to_xy(start_pos)
    (map_size_x, map_size_y) = s_to_xy(map_size)
    (velocity_x, velocity_y) = s_to_xy(velocity)
    
    if velocity_x < 0:
        velocity_x = map_size_x + velocity_x
    if velocity_y < 0:
        velocity_y = map_size_y + velocity_y

    end_pos_x = (start_pos_x + iterations * velocity_x) % map_size_x
    end_pos_y = (start_pos_y + iterations * velocity_y) % map_size_y

    return xy_to_s(end_pos_x, end_pos_y)

def get_result(raw_data):
    """
    For the part2, this code will not provide a result by itself. It's more a manual thing:
    every map is printed after a given number of seconds.
    When you see the easter egg, just type "end" instead of "enter".
    """
    total = 0

    data = read_data_custom(raw_data)
    if re.match(r'sample', args.input_file):
        map_size = "11,7"
    else:
        map_size = "101,103"

    #print_robots_on_map([x['p'] for x in data], map_size)

    for iterations in range(2, 100000, 101):
        _log("Iteration %d" % (iterations))
        end_positions = []
        for robot in data:
            end_pos = get_position_after(robot['p'], robot['v'], map_size, iterations)
            #_log("Position of robot %s: (%s)" % (robot, end_pos))
            end_positions.append(end_pos)

        print_robots_on_map(end_positions, map_size)

        # Calculate how many robots there are per quarter of map
        nb_per_quarter = {
            "0,0": 0,
            "0,1": 0,
            "1,0": 0,
            "1,1": 0
        }
        (map_size_x, map_size_y) = s_to_xy(map_size)
        mid_x = ( map_size_x - 1 ) / 2
        mid_y = ( map_size_y - 1 ) / 2
        for end_pos in end_positions:
            (rx, ry) = s_to_xy(end_pos)
            # ignore robots that are in the middle of the map
            if rx == mid_x or ry == mid_y:
                continue

            qx = min(int(rx / mid_x),1)
            qy = min(int(ry / mid_y),1)
            nb_per_quarter["%d,%d" % (qx,qy)] += 1

        a = input("Press Enter to go to next, or 'end' to finish: ")
        if a == "end":
            _log("Found a Christmas tree!")
            total = iterations
            break
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))