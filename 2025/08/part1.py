#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
import math
from collections import defaultdict

# =============================================================================
# Generic code
# =============================================================================

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, nargs='?', default="input.txt", help="Input file")
parser.add_argument('--verbose', '-v', action='count', default=0, help="Increase verbosity level")
parser.add_argument('--interactive', '-i', action='store_true', default=False, help="Run in interactive mode")


args = parser.parse_args()
if args.interactive:
    args.verbose = 0

def _log(msg, level = 1):
    if level <= args.verbose:
        print("[DEBUG] %s" % (msg))

def print_map(map, level = 1):
    output = ""
    if level <= args.verbose:
        for y in range(len(map)):
            for x in range(len(map[y])):
                output += map[y][x]
            output += "\n"
        print(output)

def print_result(result):
    if args.verbose > 0: 
        print(_c("\n================", "yellow"))
    print(_c("Result: %s" % (result), "yellow", bold=True))

if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


with open(args.input_file) as f:
    raw_data = f.read().strip()

def yx_to_s(y, x):
    return "%d,%d" % (y,x)

def s_to_yx(yx):
    (y, x) = yx.split(",")
    return (int(y), int(x))

def in_map(map, y, x):
    """
    Tell if a given location is inside (True) or outside (False) of a given map (2D array)
    """
    if y < 0 or y >= len(map):
        return False
    if x < 0 or x >= len(map[y]):
        return False
    return True

def copy_map(map):
    """
    Create a copy of a map
    """
    new_map = []
    for y in range(len(map)):
        new_map.append(map[y].copy())
    return new_map

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

def _c(text, fg=None, bg=None, bold=False, italic=False, dark=False, underline=False, reverse=False, strike=False):
    color_map = {
        "black": 0,
        "gray": 0,
        "grey": 0,
        "red": 1,
        "green": 2,
        "brown": 3,
        "yellow": 3,
        "blue": 4,
        "purple": 5,
        "cyan": 6,
        "white": 7,
    }

    colors=[]
    color_text = ""
    if bold:
      colors.append("1")
    if dark:
      colors.append("2")
    if italic:
      colors.append("3")
    if underline:
      colors.append("4")
    if reverse:
      colors.append("7")
    if reverse:
      colors.append("9")
    if fg:
        colors.append("3%d"%(color_map[fg]))
    if bg:
        colors.append("4%d"%(color_map[bg]))
    if len(colors) > 0:
        color_text = '\033[%sm' % (';'.join(colors))
    

    return "%s%s%s" % (color_text, text, '\033[0m')

# =============================================================================
# Puzzle code
# =============================================================================

def get_distance_index(distances: list, distance: int) -> int:
    """
    From a list of existing distances, sorted from shorted to longest
    Identify the index at which a given distance should be located
    Example:
        With array [1, 2, 4 , 5]
        The distance 3 should be located in position 2 (starting from 0)
    """

    l = len(distances) # length of the array of distances

    # Handle specific case: length = 0
    if l == 0:
        return 0
    
    # Handle specific case: length = 1
    if l == 1:
        if distance < distances[0]:
            return 0
        else:
            return 1
        
    
    # Handle specific cases (first and last position)
    if distance <= distances[0]:
        return 0
    elif distance >= distances[l-1]:
        return l

    # With more than 1 item in distances array, use a dicotomy algorithm for performance
    p = int(l / 2) - 1# Current position (round to lower number so we know that p+1 exists)
    min_p = 0
    max_p = l-1
    while True:
        # if our distance is between the 2 we are checking -> we are at the right position
        if distance >= distances[p] and distance <= distances[p+1]:
            return p + 1
        
        # if distance is < current position, reduction position
        if distance < distances[p]:
            max_p = p
        elif distance > distances[p]:
            min_p = p

        p = min_p + int((max_p - min_p)/2)
        if p >= l - 1:
            return l - 1

        
    return -1
        
#def add_connection(connections, a, b):
#    """
#    Add the connection between a and b into connections_dict.
#    In case a or b is already connected to other boxes, ensure that
#    it updates the exitsing connection.
#    Return the index where connection has been added into connections array.
#    """
#
#    for i in connections:
#        if a in connections[i]:
#            connections[i].append(b)
#            return i
#        elif b in connections[i]:
#            connections[i].append(a)
#            return i
#    
#    # If we're here, neither a or b are present in existing connections.
#    # Create a new one
#    connections.append([a, b])
#    return len(connections) - 1
#
#def del_connection(connections, a, b):
#    """
#    Remove a given connection 
#    """
    
def get_circuits(connections, max_junctions):
    """
    From an array of connections, containing tuples like (a,b), where a
    and b are ID of boxes, return an array of crcuits. Each circuit is an array
    of box ID which are connected together.
    If max_junctions is provided, only use this number of junctions to define circuits.
    Note: if 2 connected box are already part of a circuit, they will be skipped and will
    note be counted in max_junction.
    Example:
    input:  [(1, 2), (2, 3), (3, 4), (6, 7), (7, 8)]
    return: [[1, 2, 3, 4], [6, 7, 8]]
    """

    # 1st step: create circuits based on all junctions
    circuits = []
    cur_junctions = 0
    for (a,b) in connections:
        found_flag = False
        for i in range(len(circuits)):
            if a in circuits[i] and b in circuits[i]:
                # Nothing happen: both boxes were already in group
                found_flag = True
                #cur_junctions -= 1
                break
            elif a in circuits[i]:
                circuits[i].append(b)
                found_flag = True
                break
            elif b in circuits[i]:
                circuits[i].append(a)
                found_flag = True
                break
        if not found_flag:
            circuits.append([a,b])
        cur_junctions += 1

        if cur_junctions >= max_junctions:
            _log("Reached %d junctions. break!" % (cur_junctions))
            break

    _log("Crcuits before merge: %s" % (circuits))

     # 2nd step: Check if a box is not in 2 circuits. In which case, merge these circuits together
    change_flag = True
    while change_flag:
        change_flag = False
        for i in range(len(circuits)):
            c = circuits[i]
            for b in c:
                for j in range(i + 1, len(circuits)):
                    c2 = circuits[j]
                    if b in c2:
                        # All that circuit will be merged with the other
                        _log("Merging:",2)
                        _log("- Box %d" % (b), 2)
                        _log("- circuit %s" % (c2), 2)
                        _log("- circuit %s" % (c), 2)
                        circuits[i] += c2
                        del(circuits[j])
                        _log("- New circuit %s" % (circuits[i]), 2)
                        change_flag = True
                        break
                if change_flag:
                    break
            if change_flag:
                break

    # 3rd step: deduplicate boxes inside of each circuit
    circuits = [list(set(x)) for x in circuits]
    
    _log("Circuits after merge: %s" % (circuits))
    return circuits
        

def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    max_junctions = 1000

    # Logic of this puzzle:
    # =====================
    #
    # Parse all junction boxes and calculate the difference with other junction boxes
    # Save in an array with a size of 1000 maximum the distance between 2 junction boxes
    # The array is sorted by distance, from the shortest to the longest
    # Everything above 1000 is ignores
    # The distance is calculated with this formulae:
    #   d = sqrt((x2 - x1)² + (y2 - y1)² + (z2 - z1)²

    # First, register coordonate of all junction boxes
    # Each item of the array is a box and is represented as a 3-tuple (x, y z)
    boxes = []
    for line in raw_data.split("\n"):
        boxes.append(tuple([int(x) for x in line.split(",")]))

    # We are using sample data
    if len(boxes) < 100:
        max_junctions = 10
    
    # Create an array with distances between boxes. We'll use it to compare distances
    distances = []
    # Create an array with the X boxes that are connected together with the given distance
    # The index of items in this array must be the same as in `distances` array
    connections = []

    # Now, parse all boxes together
    for i in range(len(boxes) - 1):
        for j in range(i+1, len(boxes)):
            b1 = boxes[i]
            b2 = boxes[j]

            # Calculate the distance
            distance = int(math.sqrt(math.pow(b2[0] - b1[0], 2) + math.pow(b2[1] - b1[1], 2) + math.pow(b2[2] - b1[2], 2)))

            _log("Connection #%04d (%d,%d,%d)<->#%04d (%d,%d,%d): d=%d" % (
                i, b1[0], b1[1], b1[2],
                j, b2[0], b2[1], b2[2],
                distance
            ), 3)

            # Identify position
            idx = get_distance_index(distances, distance)
            if idx >= 2 * max_junctions:
                _log("Connection #%04d (%d,%d,%d)<->#%04d (%d,%d,%d): distance is too big (d=%d, idx=%d)" % (
                    i, b1[0], b1[1], b1[2],
                    j, b2[0], b2[1], b2[2],
                    distance, idx
                ), 3)
                continue

            distances.insert(idx, distance)
            connections.insert(idx, (i, j))

            _log("Connection #%04d (%d,%d,%d)<->#%04d (%d,%d,%d): d=%d idx=%d" % (
                i, b1[0], b1[1], b1[2],
                j, b2[0], b2[1], b2[2],
                distance, idx
            ), 3)

            # Keep 2 x the maximum number of junctions, because we might skip some 
            if len(distances) > 2 * max_junctions:
                d = distances.pop()
                (c1, c2) = connections.pop()
                b1 = boxes[c1]
                b2 = boxes[c2]
                _log("Removing connection  #%04d (%d,%d,%d)<->#%04d (%d,%d,%d): d=%d" % (
                    c1, b1[0], b1[1], b1[2],
                    c2, b2[0], b2[1], b2[2],
                    d
                ), 3)

    
    _log("Distances: %s" % (distances))
    _log("Connections: %s" % (connections))
    
    # Now that we have all closest connections, calculate the one that are groupped together
    circuits = get_circuits(connections, max_junctions)

    # Sort circuits by number of items in it
    circuits.sort(key=len, reverse=True)
    _log("Found circuits: %s" % (circuits))

    for i in range(len(circuits)):
        c = circuits[i]
        for b in c:
            for j in range(i+1, len(circuits)):
                c2 = circuits[j]
                for b2 in c2:
                    if b == b2:
                        _log("same box found in 2 circuits: %d %d" % (b, b2))
                        _log("%s" % (c))
                        _log("%s" % (c2))

    # Take size of 3 largest circuits and multiply them together
    total = 1
    for g in circuits[0:3]:
        total *= len(g)
        _log("Found group of size %d. new total = %d" % (len(g), total))
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))