#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
import math

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
        print("\n================")
    print("Result: %s" % (result))

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

def _c(text, fg=None, bg=None):
    color_map = {
        "black": 0,
        "red": 1,
        "green": 2,
        "brown": 3,
        "yellow": 3,
        "blue": 4,
        "purple": 5,
        "cyan": 6,
        "gray": 7,
    }

    colors=[]
    color_text = ""
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

def consolidate(ranges):

    consolidated_ranges = ranges

    global_flag = False
    for f in ranges:
        s = f["start"]
        e = f["end"]
        _log(" >> Evaluating fresh ingredient ID range %d-%d" % (s, e), 3)

        nb_myself = 0
        for c in consolidated_ranges:
            # don't compare me and myself
            if c == f:
                nb_myself += 1
                if nb_myself > 1:
                    _log("  [%s] Remove duplicate range %s-%s" % (_c("-", "red"), s, e))
                    global_flag = True
                    consolidated_ranges.remove(c)
                continue

            consolidated_flag = False
            # Check if start if current range is included in the consolidated range
            if s >= c["start"] and s <= c["end"]:
                consolidated_flag = True
                s = c["start"]
                _log("  [i] Lower the start boundary to %d after evaluation with range %s-%s" % (s, s, c["end"]), 3)
            # Same with end
            if e >= c["start"] and e <= c["end"]:
                consolidated_flag = True
                e = c["end"]
                _log("  [i] increase the end boundary to %d after evaluation with range %s-%s" % (e, c["start"], e), 3)
            
            # IF after this process, current range is the same as the range we are checking, just remove it
            if s == c["start"] and e == c["end"]:
                # we can ignore this range as it is already present in list of consolidated range
                _log("  [%s] Ignoring range %s-%s as it is part of consolidated range %s-%s" % (_c("-", "red"), f["start"], f["end"], c["start"], c["end"]), 2)
                consolidated_ranges.remove(f)
                global_flag = True
                break
            # Otherwise, if we do have something in common with the range, add the new range and remove the other
            elif consolidated_flag:
                global_flag = True
                _log("  [%s] Adding new consolidated range: %s-%s" % (_c("+", "green"), s,e), 2)
                consolidated_ranges.append({"start": s, "end": e})
                _log("  [%s] Removing old consolidated range: %s-%s" % (_c("-", "red"), c["start"], c["end"]), 2)
                consolidated_ranges.remove(c)
                break
        if not consolidated_flag:
            _log("  [%s] Keeping the range in list of consolidated range" % (_c("~", "brown")))

    return (global_flag, consolidated_ranges)

def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    # parse the input. Store list of fresh ingredient ID ranges
    fresh_id_ranges = []
    for line in raw_data.split("\n"):
        if line == "":
            continue
        if "-" in line:
            (start, end) = line.split("-") 
            fresh_id_ranges.append({"start": int(start), "end": int(end)})


    # Now, from the list of ingredient ID ranges, get a consolidated list which
    # takes into account overlapses.
    # For example, if we have 3-10 and 7-12, it will merge the 2 ranges in a single range 3-12
    # If we have 3-10 and 5-8, it will keep only the range 3-10
    result = True
    consolidated_ranges = fresh_id_ranges
    nb = 0
    while result:
        _log("%s" % _c(" === Consolidating ranges [#%d]===" % (nb+1), "blue"))
        _log(_c("%d ranges **before** consolidation" % (len(consolidated_ranges)), "cyan"))
        (result, consolidated_ranges) = consolidate(consolidated_ranges)
        _log(_c("%d ranges **after** consolidation" % (len(consolidated_ranges)), "cyan"))
        nb += 1
    
    _log(_c("No more consolidation possible, after %d successfull consolidations" % (nb-1), "green"))
        
    # Sort ranges
    consolidated_ranges.sort(key=lambda x: x["start"])

    _log("List of consolidated ranges:")
    for c in consolidated_ranges:
        _log("  - %s-%s" % (c["start"], c["end"]))

    # Count total of ingredient in all consolidated ranges
    for c in consolidated_ranges:
        nb = c["end"] - c["start"] + 1
        total += nb
        _log("Adding %15d items from range %15s-%-15s (total: %d)" % (nb, c["start"], c["end"], total))

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))