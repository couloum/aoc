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

def print_result(result1, result2):
    if args.verbose > 0: 
        print("\n================")
    print("Result part 1: %s" % (result1))
    print("Result part 2: %s" % (result2))

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

#
# Main function
#
def get_results(raw_data):
    """
    Parse the map and identify coordonates of all antenna, by letter.
    For each letter of antenna, identify all possible pairs of coordonates.
    Set in another map the location of each antinode
    """
    total1 = 0
    total2 = 0

    map = read_data_map(raw_data)

    # 1 - Get coordonates of all antennas
    
    # Dictionnary of all coordonates of all antennas, per antenna symbol
    antennas_coord = dict()

    for x in range(len(map)):
        for y in range(len(map[x])):
            symbol = map[x][y]

            # Skip locations with no antenna
            if symbol == ".":
                continue

            if not symbol in antennas_coord:
                antennas_coord[symbol] = []

            (antennas_coord[symbol]).append(xy_to_s(x,y))

    _log("List of antennas coordonates: %s" % (antennas_coord))

    
    # 2 - create all pairs of coordonates per antenna symbol
    coord_pairs = dict()

    for symbol, coords in antennas_coord.items():
        coord_pairs[symbol] = []

        for i in range(len(coords)-1):
            for j in range(i+1,len(coords)):
                (coord_pairs[symbol]).append("%s-%s" % (coords[i], coords[j]))
    
    _log("List of coordonates pairs: %s" % (coord_pairs))

    # 3 - For each coordonates pair, calculate antinodes

    # Create a new map for antinodes as a copy of original map
    antinodes_map = copy_map(map)
    
    for symbol, pairs in coord_pairs.items():
        for coord_pair in pairs:
            (coord1, coord2) = coord_pair.split("-")
            (x1, y1) = s_to_xy(coord1)
            (x2, y2) = s_to_xy(coord2)
            
            # if antennas are not recovered by an antinode, add them to the total for part 2
            if type(antinodes_map[x1][y1]) == str:
                total2 += 1
                antinodes_map[x1][y1] = 0
            if type(antinodes_map[x2][y2]) == str:
                total2 += 1
                antinodes_map[x2][y2] = 0

            # Add antinodes for each pair of atennas.
            for i in range(2):
                # Calculate diff between x and y of the 2 antennas
                # Note: we know that x1,y1 has always been seen first in the map, due to how coordonates were
                #       identified and paired in steps 1 and 2.
                if i == 0:
                    # First, add antinodes on the North or West.
                    (a1_x, a1_y) = (x1, y1)
                    (dx, dy) = (x2 - x1, y2 - y1)
                else: # i == 1
                    # Then, add antinodes on the South or East.
                    (a1_x, a1_y) = (x2, y2)
                    (dx, dy) = (x1 - x2, y1 - y2)

                nb = 0 # Number of antinodes positionned.
                while True:
                    # Get coordonates of antinode, based on last antinode position
                    (a1_x, a1_y) = (a1_x - dx, a1_y - dy)

                    if not in_map(antinodes_map, a1_x, a1_y):
                        # If outside of the map, we can stop calculation
                        break

                    # If still inside the map and not already an antinode, set the point
                    nb += 1
                    if nb == 1:
                        # If there's alreay an antinode on the location, see what type it is
                        if (type(antinodes_map[a1_x][a1_y]) == int):
                            cur_nb = antinodes_map[a1_x][a1_y]
                            if cur_nb != 1:
                                antinodes_map[a1_x][a1_y] = nb
                                _log("  => [OK] Set antinode %d at position (%s,%s). total1=%d total2=%d" % (nb, a1_x,a1_y,total1, total2), 3)
                                total1 += 1
                            else: # cur_nb != 1
                                _log("  => [^^] Already an antinode at position [%s,%s]. total1=%d total2=%d" % (a1_x,a1_y,total1, total2), 3)
                        else: # (type(antinodes_map[a1_x][a1_y]) == int)
                            antinodes_map[a1_x][a1_y] = nb
                            _log("  => [OK] Set antinode %d at position (%s,%s). total1=%d total2=%d" % (nb, a1_x,a1_y,total1, total2), 3)
                            total1 += 1
                            total2 += 1
                    else: # nb ==1
                        if (type(antinodes_map[a1_x][a1_y]) == int):
                            _log("  => [^^] Already an antinode at position [%s,%s]. total1=%d total2=%d" % (a1_x,a1_y,total1, total2), 3)
                        else:
                            antinodes_map[a1_x][a1_y] = nb
                            _log("  => [OK] Set antinode %d at position (%s,%s). total1=%d total2=%d" % (nb, a1_x,a1_y,total1, total2), 3)
                            total2 += 1

                


    _log("Map of antinodes:", 2)
    print_map(antinodes_map, 2)

    antinodes_map_part1 = []
    antinodes_map_part2 = []
    for x in range(len(antinodes_map)):
        tmp1 = []
        tmp2 = []
        for y in range(len(antinodes_map[x])):
            char1 = "."
            char2 = "."
            if map[x][y] != ".":
                char1 = map[x][y]
                char2 = map[x][y]
            if type(antinodes_map[x][y]) == int:
                if antinodes_map[x][y] == 1:
                    char1 = map[x][y] = "#"
                    char2 = map[x][y] = "#"
                elif antinodes_map[x][y] > 1:
                    char2 = map[x][y] = "#"
            tmp1.append(char1)
            tmp2.append(char2)
        antinodes_map_part1.append(tmp1.copy())
        antinodes_map_part2.append(tmp2.copy())
                
    _log("Map for part 1")
    print_map(antinodes_map_part1)
    _log("Map for part 2")
    print_map(antinodes_map_part2)


    return (total1, total2)
    
   
# Do not remove me
(res1, res2) = get_results(raw_data)
print_result(res1, res2)