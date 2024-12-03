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
    data = []
    for line in raw_data.split("\n"):
        data += [x+")" for x in line.split(")")]

    return data

#
# Main function
#
def get_result(raw_data):
    total = 0
    data = read_data_custom(raw_data)

    regex = re.compile(r".*mul\((\d+),(\d+)\).*")

    for formulae in data:
        result = regex.match(formulae)
        if result:
            (a, b) = (int(result.group(1)), int(result.group(2)))
            total += a*b
            _log("[OK] %s -> %d * %d = %d / total=%d" % (formulae, a, b, a*b, total))
        else:
            _log("[!!] %s ignored" % (formulae))

    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
