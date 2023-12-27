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

    for item in puzzle:
        hash = get_hash(item)
        total += hash
        _log("hash of string %s is %d. New total=%d" % (item, hash, total))
    

    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
