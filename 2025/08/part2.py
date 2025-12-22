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
    From a list of existing distances, sorted from shortest to longest
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
    
def get_when_one_circuit(connections: list, expected_boxes: int) -> int:
    """
    From an array of connections, containing junctions in form of tuples like (a,b), where a
    and b are ID of boxes, return when we form a single big circuit. 
    Example:
    inputs:
        connections: [ (1, 2), (2, 3), (3, 4), (6, 7), (7, 8), (8, 9), (8, 5), (8, 6), (5, 2), (5, 3) ]
        expected_boxes: 9
    return: 8 (the index)
    """

    # Internal logic:
    # - case A: If none of the 2 boxes are in any circuit, create a new circuit
    # - case B: If the 2 boxes are already in a circuit, do nothing
    # - case C: If one of the 2 boxes only is already in one circuit only, add the other box in the same circuit
    # - case D: If one box is in one circuit and the other is in another circuit, merge the 2 circuits
    circuits = []
    cur_junctions = 0
    seen_boxes = {}
    for (a,b) in connections:
        found_circuit = {'a': None, 'b': None}
        seen_boxes[a] = True
        seen_boxes[b] = True
        # Check if boxes a and b are present in any circuit
        for i in range(len(circuits)):
            if a in circuits[i]:
                found_circuit['a'] = i
            if b in circuits[i]:
                found_circuit['b'] = i
            if found_circuit['a'] and found_circuit['b']:
                break
        
        _log("Evaluating connection %s (%s,%s): a=%s b=%s" % (_c(f"#{cur_junctions}", "blue"), a, b, found_circuit['a'], found_circuit['b']), 2)
        # Case A: If none of the 2 boxes are in any circuit
        if found_circuit['a'] == None and found_circuit['b'] == None:
            # Create new circuit
            _log("  Case A: create a new circuit: %s" % ([a,b]), 2)
            circuits.append([a,b])
        
        # Case B: If the 2 boxes are already in a circuit
        elif found_circuit['a'] == found_circuit['b']:
            # do nothing
            _log("  Case B: do nothing: %s" % (circuits[found_circuit['a']]), 2)
        
        # Case C: If one of the 2 boxes only is already in one circuit only
        elif found_circuit['a'] == None or found_circuit['b'] == None:
            # add the other box in the same circuit
            if found_circuit['a'] != None:
                box_found = a
                box_to_append = b
                circuit_to_update = found_circuit['a']
            else:
                box_found = b
                box_to_append = a
                circuit_to_update = found_circuit['b']

            circuits[circuit_to_update].append(box_to_append)
            _log("  Case C: found box %d in circuit #%d. Add box %d to it: %s" % (box_found, circuit_to_update, box_to_append, circuits[circuit_to_update]), 2)
       
        # Case D: If one box is in one circuit and the other is in another circuit
        else:
            # merge the 2 circuits
            circuits[found_circuit['a']] += circuits[found_circuit['b']]
            circuits[found_circuit['b']] = []
            _log("  Case D: Merge circuit %d into %d: %s" % (found_circuit['b'], found_circuit['a'], circuits[found_circuit['a']]), 2)


        # Remove empty circuits
        while [] in circuits:
            circuits.remove([])

        _log("  Circuits: %s" % (circuits), 2)
        

        if len(seen_boxes.keys()) == expected_boxes:
            if len(circuits) == 1:
                _log("seen_boxes: %s" % (seen_boxes.keys()))
                _log("One big circuit: %s" % (sorted(circuits[0])))
                return cur_junctions
            
        cur_junctions += 1
            
    _log("Circuits: %s" % (circuits))

    return None
        

def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

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

    max_junctions = 8 * len(boxes)
    
    # Create an array with distances between boxes. We'll use it to compare distances
    distances = []
    # Create an array with the X boxes that are connected together with the given distance
    # The index of items in this array must be the same as in `distances` array
    connections = []

    # Now, parse all boxes together
    for i in range(len(boxes) - 1):
        _log("Evaluating box ID %d with others" % (i))
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
            if idx >= max_junctions:
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

            if len(distances) > max_junctions:
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
    
    # Now that we have all closest connections, calculate when we form 1 big circuit with all boxes
    junction_idx = get_when_one_circuit(connections, len(boxes))
    if not junction_idx:
        print("Error: not enough junctions to form one big circuit with all boxes")
        sys.exit(1)
    
    _log("Junction ID that connect all boxes: %d" % (junction_idx))
    
    # Get x coordonate of each box. That's the total
    box_a = connections[junction_idx][0]
    box_b = connections[junction_idx][1]

    _log("Boxes in that junction: (%d,%d)" % (box_a, box_b))
    _log("Coordonate of boxes:")
    _log("- A: (%d, %d, %d)" % (boxes[box_a]))
    _log("- B: (%d, %d, %d)" % (boxes[box_b]))

    total = boxes[box_a][0] * boxes[box_b][0]
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))