#!/usr/bin/env python3

import argparse
import re
import os
import sys
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
    _map = {}
    for line in lines:
        matches = re.fullmatch("^([0-9A-Z]{3}) = \(([0-9A-Z]{3}), ([0-9A-Z]{3})\)", line)
        _map[matches.group(1)] = (matches.group(2), matches.group(3))

    _log("Left/Right instructions: %s" % (lr_instructions))
    _log("Map:")
    for item in _map.items():
        _log("  %s = (%s, %s)" % (item[0], item[1][0], item[1][1]))

    return (lr_instructions, _map)


def part2(raw_data):
    total = 0
    (lr_instructions, _map) = read_data(raw_data)

    # Identify all keys ending with a A
    starting_positions = list(map(lambda x: x[0], list(filter( lambda x: True if x[0].endswith("A") else False, _map.items()))))
    nb_starting_positions = len(starting_positions)
    nb_steps_to_arrival = [ 1 for i in range(nb_starting_positions)]

    _log("Found %d starting positions: %s" % (nb_starting_positions, starting_positions))
    

    for pos_idx in range(nb_starting_positions):
        end_flag = False
        nb_steps = 1
        while not end_flag:
            for inst in lr_instructions:
                _log("(%03d) Processing instruction '%s'" % (nb_steps, inst), 2)
                dir = 0 if inst == "L" else 1
                nb_arrived = 0
                
                cur_pos = starting_positions[pos_idx]

                next_pos = _map[cur_pos][dir]
                _log("(%03d-%02d) Current position: %s = %s" % (nb_steps, pos_idx, cur_pos, _map[cur_pos]), 3)
                _log("(%03d-%02d) New position:     %s" % (nb_steps, pos_idx, next_pos), 3)

                if (next_pos.endswith("Z")):
                    _log("Starting Position #%d arrived in %d steps" % (pos_idx, nb_steps))
                    end_flag = True
                    break

                nb_steps += 1
                starting_positions[pos_idx] = next_pos
            
        nb_steps_to_arrival[pos_idx] = nb_steps
                

    _log("Nb steps: %s" % (nb_steps_to_arrival))

    # Find common greatest factor of all numbers in the array
    # Take greatest item from nb_steps_to_arrival
    # Multiply it untill it is dividable by all other items
     
    nb_steps_to_arrival.sort()
    max_steps = nb_steps_to_arrival[-1]
    _log("Maximum number of steps is %d" % (max_steps))

    tmp = max_steps
    end_flag = False
    while not end_flag:
        tmp += max_steps
        step_end_flag = True
        for i in nb_steps_to_arrival[0:-1]:
            if (tmp % i) != 0:
                step_end_flag = False
                break
        if step_end_flag:
            _log("Found steps: %s" % (tmp))
            break

    total = tmp

    return total


result = part2(raw_data)
print_result(result)

        
        
