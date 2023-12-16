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
    data = []
    for line in raw_data.split("\n"):
        data.append([int(x) for x in line.split(" ")])

    _log("Data:")
    for i in data:
        _log("  %s" % (i))
    
    return data

def find_next_value(history):
    end_flag = False
    nb_steps = 0
    last_reduction = [x for x in history] # Reduction is an history after diff of all items
    last_items = []
    while not end_flag:
        last_reduction_diff = []
        last_items.append(last_reduction[-1])
        _log("#%02d: %s" % (nb_steps, last_reduction), 2)
        nb_steps += 1

        for idx in range(len(last_reduction) - 1):
            diff = last_reduction[idx+1] - last_reduction[idx]
            last_reduction_diff.append(diff)
        
        last_reduction = last_reduction_diff
        # End if all values are 0
        if max(last_reduction) == 0 and min(last_reduction) == 0:
            _log("All values are 0. Stop after %d steps" % (nb_steps), 2)
            end_flag = True
            break


    # Append a last 0 to the last work array containing all 0
    #last_reduction.append(0)

    # Now, for each step, reconstitue numbers, based on last number
    _log("Reconstitue next numbers based on last items: %s" % (last_items), 2)
    cur_diff = 0
    for step in range(nb_steps):
        cur_last_item = last_items[-(step+1)]
        new_last_item = cur_last_item + cur_diff
        cur_diff = new_last_item
        _log("Step #%d - Reconstituted history: %s" % (step, new_last_item), 2)

    _log("Next value of %s is %d" % (history, new_last_item))
    return new_last_item


def part1(raw_data):
    total = 0
    histories = read_data(raw_data)
    
    for history in histories:
        _log("============================================================", 2)
        _log("Processing history %s" % (history), 2)
        _log("============================================================", 2)
        total += find_next_value(history)
        _log("Current total: %d" % (total))
    
    return total


result = part1(raw_data)
print_result(result)

        
        
