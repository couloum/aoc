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

    return data


def do_cycle(puzzle, nb_cycles=1):
    # Every time, we'll move rocks to the east. We must rotate puzzle
    # accordingly.
    # Wanted tilt directions:
    # - North (rotate -90°)
    # - West (rotate +90°)
    # - South (rotate +90°)
    # - East (rotate +90°)
    # Then rotate +180° to get north back to it's position

    puzzle = np.rot90(puzzle, k=1, axes=(0,1))

    for cycle in range(0, nb_cycles):
        for tilt in range(0, 4):
            # Then, move to the left all "0" as much as possible
            for line in puzzle:
                free_idx = -1
                for idx in range(len(line)):
                    item = line[idx]
                    if item == ".":
                        # Search for next O and move it to this position
                        for j in range(idx+1, len(line)):
                            item2 = line[j]
                            if item2 == "#":
                                break
                            if item2 == "O":
                                line[idx] = "O"
                                line[j] = "."
                                break

            puzzle = np.rot90(puzzle, k=1, axes=(1,0))
            
        #_log("Map after tilt #%d:" % (cycle+1), 2)
        #print_map(np.rot90(puzzle, k=cycle, axes=(0, 1)), 2)
                        
    # Finally rotate again +90°
    puzzle = np.rot90(puzzle, k=1, axes=(1,0))

    return puzzle

def puzzle_to_string(puzzle):
    result = ""
    for line in puzzle:
        for char in line:
            result += char
        result += "N"

    return result

#
# Main function
#
def get_result(raw_data):
    total = 0
    _puzzle = read_data_map(raw_data)

    _log("Map before:")
    print_map(_puzzle)

    # Find after how many cycles, we get back to a known position
    puzzles_history = [puzzle_to_string(_puzzle)]
    cycles_loop_start=0
    cycles_loop_end=0
    cycles_loop_int=0
    for cycle in range(1, 10000000001):
        _puzzle = do_cycle(_puzzle, 1)
        _puzzle_str = puzzle_to_string(_puzzle)
        if _puzzle_str in puzzles_history:
            cycles_loop_start=puzzles_history.index(_puzzle_str)
            cycles_loop_end=cycle
            cycles_loop_int=cycles_loop_end-cycles_loop_start
            _log("After %d cycles, we get back to position from cycle %d. Loop of %d cycles." % (cycles_loop_end, cycles_loop_start, cycles_loop_int))
            _log(_puzzle_str)
            break
        puzzles_history.append(_puzzle_str)

    # Now, we calculate how many cycles we need to
    full_loops = math.floor((1000000000 - cycles_loop_start) / cycles_loop_int)
    remaining_cycles = (1000000000 - cycles_loop_start) % full_loops
    _log("1000000000 cycles = %d init cycles + %d loops of %d cycles + %d remaining cycles" % (cycles_loop_start, full_loops, cycles_loop_int, remaining_cycles))
    _puzzle = do_cycle(_puzzle, remaining_cycles)

    _log("Map after 1000000000 cycles:")
    print_map(_puzzle)

    # Now count score
    for idx in range(len(_puzzle)):
        score = len(_puzzle) - idx
        nb_rocks = list(_puzzle[idx]).count("O")
        total += (nb_rocks * score)
        _log("Found %d rocks on line %d (score=%d). Adding %d to total. New total: %d" % (nb_rocks, idx, score, (nb_rocks*score), total))

    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
