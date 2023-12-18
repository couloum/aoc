#!/usr/bin/env python3

import argparse
import re
import os
import sys
import numpy as np
import math

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

# =============================================================================
# Puzzle code
# =============================================================================

def read_data(raw_data):
    data = []
    for line in raw_data.split("\n"):
        data.append([x for x in line])

    _log("Data:")
    print_map(data, 1)
    
    return data

def expand_map(_map):

    # Create the new map
    _new_map = np.array(_map, copy=True)

    # Expand twice lines without any galaxy. After each expansion swap the map.
    for i in range(2):
        idx = 0
        while idx < (len(_new_map)):
            if '#' in _new_map[idx]:
                idx+=1
                continue
            _log("No galaxy found in line with idx %d: %s" % (idx, _new_map[idx]), 2)
            # In case there's no galaxy on this line, replace all "." per a x to mark an hyper jump
            _new_map[idx] = [ "x" for x in _new_map[idx] ]
            idx += 1
        _new_map = np.swapaxes(_new_map, 1, 0)

    return _new_map

def number_galaxies(_map):
    """
    Replace each galaxy with a unique number
    """
    num = 0
    for x in range(len(_map)):
        for y in range(len(_map[0])):
            if _map[x][y] == "#":
                _map[x][y] = num
                num += 1

    return _map

def get_galaxies_pairs(_map):
    """
    Return a list of tupes with pairs of galaxies.
    Each galaxy is represented by its coordonate in form of a tuple (x, y).
    This is an exemple of return:
    [ ((1, 1), (2, 3)), ((1, 1), (4, 5)) ]
    This means that galaxy at coordonates x=1,y=1 is paired with galaxies at coordonates x=2,y=3 and x=4,y=5
    """

    pairs_list = []

    for x in range(len(_map)):
        for y in range(len(_map[0])):
            if _map[x][y] == "." or _map[x][y] == "x":
                continue
            # We've found a galaxy. Now, pair it will all other galaxies
            # Only parse galaxies after this one
            for x2 in range(x, len(_map)):
                for y2 in range(len(_map[0])):
                    if x == x2 and y2 <= y:
                        # Don't pair with itself
                        continue
                    if _map[x2][y2] == "." or _map[x2][y2] == "x":
                        continue
                    # We've found a galaxy to pair with
                    _log("Found a pair of galaxies %s<->%s // (%d,%d)<->(%d,%d)" % (_map[x][y], _map[x2][y2], x, y, x2, y2), 2)
                    pairs_list.append(((x,y), (x2,y2)))

    return pairs_list



def part2(raw_data):
    total = 0
    _map = read_data(raw_data)
    
    _log("Satrting universe expansion")
    _map = expand_map(_map)
    _log("End of universe expansion")
    
    _log("Map after universe expansion:")
    print_map(_map)

    _log("Numbering galaxies")
    _map = number_galaxies(_map)

    _log("Map after galaxies numbering:")
    print_map(_map)

    _log("Get list of pairs of galaxies")
    pairs_list = get_galaxies_pairs(_map)
    _log("Found %d pairs of galaxies in the universe" % (len(pairs_list)))

    hyperjump_nb = 1000000
    for pair in pairs_list:
        (x, y)=pair[0]
        (x2, y2)=pair[1]
        distance = math.fabs(x2 - x) + math.fabs(y2 - y)
        # Check if there are hyper space jumps between galaxies
        if x != x2:
            for xx in range(x, x2, int((x2 - x) / math.fabs(x2 - x))):
                if _map[xx][0] == "x":
                    _log("Vertical hyperspace jump between %s and %s" % (_map[x][y], _map[x2][y2]), 2)
                    distance += hyperjump_nb -1
        if y != y2:
            for yy in range(y, y2, int((y2 - y) / math.fabs(y2 - y))):
                if _map[0][yy] == "x":
                    _log("Horizonal hyperspace jump between %s and %s" % (_map[x][y], _map[x2][y2]), 2)
                    distance += hyperjump_nb -1
        _log("Distance between %s and %s is %d" % (_map[x][y], _map[x2][y2], distance))
        total += distance
    
    return int(total)


result = part2(raw_data)
print_result(result)

        
        
