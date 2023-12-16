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
    lines = raw_data.split("\n")
    lr_instructions = lines[0]
    lines = lines[2:]
    map = {}
    for line in lines:
        matches = re.fullmatch("^([A-Z]{3}) = \(([A-Z]{3}), ([A-Z]{3})\)", line)
        map[matches.group(1)] = (matches.group(2), matches.group(3))

    _log("Left/Right instructions: %s" % (lr_instructions))
    _log("Map:")
    for item in map.items():
        _log("  %s = (%s, %s)" % (item[0], item[1][0], item[1][1]))

    return (lr_instructions, map)


def part1(raw_data):
    total = 0
    (lr_instructions, map) = read_data(raw_data)
    
    cur_pos = "AAA"
    end_flag = False
    nb_steps = 1
    while not end_flag:
        for inst in lr_instructions:

            _log("(%03d) Processing instruction '%s'" % (nb_steps, inst), 2)

            dir = 0 if inst == "L" else 1

            next_pos = map[cur_pos][dir]
            _log("(%03d) Current position: %s = %s" % (nb_steps, cur_pos, map[cur_pos]), 3)
            _log("(%03d) New position:     %s" % (nb_steps, next_pos), 3)

            if (next_pos == "ZZZ"):
                _log("You have arrived to destination in %d steps!" % (nb_steps))
                end_flag = True
                break
            nb_steps += 1
            cur_pos = next_pos

    total = nb_steps
    return total


result = part1(raw_data)
print_result(result)

        
        
