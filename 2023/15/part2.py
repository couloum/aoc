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

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

# =============================================================================
# Puzzle code
# =============================================================================

def read_data_custom(raw_data):
    #data = []

    return raw_data.split(",")

def get_hash(input):
    hash = 0
    for c in input:
        hash += ord(c)
        hash *= 17
        hash %= 256

    return hash

#
# Main function
#
def get_result(raw_data):
    total = 0
    puzzle = read_data_custom(raw_data)

    boxes = [ [] for x in range(0, 256)]
    lenses = {}
    for item in puzzle:
        (label, action) = re.search("^([a-z]+)([-=])", item).groups()
        position = get_hash(label)
        lens = int(item[-1]) if action == "=" else 0

        _log("label=%s position=%s action='%s' lens=%s" % (label, position, action, lens), 3)

        box = boxes[position]

        if action == "-":
            if label in box:
                box.remove(label)
        elif action == "=":
            if not label in box:
                box.append(label)
            lenses[label] = lens
            _log("Add label %s in box %d" % (label, position), 2)
        
        boxes[position] = box

        _log("After %s" % (item))
        for idx in range(len(boxes)):
            box = boxes[idx]
            if len(box) > 0:
                _log("Box %d: %s" % (idx, " ".join(["[%s %d]" % (x, lenses[x]) for x in box])))
        
        
    _log("Calculate focusing power")
    for box_idx in range(len(boxes)):
        box = boxes[box_idx]
        for slot in range(1, len(box)+1):
            label = box[slot-1]
            score = (1+box_idx) * slot * lenses[label]
            total += score
            _log("%s: %d (box %d) * %d (slot) * %d (focal) = %d. Total=%d" % (label, box_idx+1, box_idx, slot, lenses[label], score, total))
                
        
    

    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
