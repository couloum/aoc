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

def render_map(map, info):
    # Clear the screen and move the cursor to the top-left
    sys.stdout.write("\033[H\033[J")
    print(info)
    print("----------------------------------------------------------------------")
    output = ""
    for y in range(len(map)):
        for x in range(len(map[y])):
            color = "white"
            if map[y][x] == "|":
                color = "red"
            elif map[y][x] == "^":
                color = "yellow"
            output += _c(map[y][x], color)
        output += "\n"
    print(output)
    sys.stdout.flush()

def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    map = read_data_map(raw_data)

    # Replace "S" from 1st line with a "|" character
    i = map[0].index("S")
    map[0][i] = "|"

    render_map(map, "Total: 0")

    # Now, process line by line with this logic:
    # - If current pos is ".", check symbol above
    #   - If it was a ".", do nothing
    #   - If it was a "|", replace with "|"
    # - If current pos is "^", replace direct left and right positions with "|"
    #
    # We assume this:
    # - There is always at least 1 "." between each "^" character
    # - There is not "^" character on the boarder of the map

    # Start parsing at line 1 (and not 0)
    for y in range(1, len(map)):
        for x in range (len(map[y])):
            if map[y][x] == ".":
                if map[y-1][x] == "|":
                    # Beam if following its path
                    map[y][x] = "|"
            elif map[y][x] == "^":
                if map[y-1][x] == "|":
                    # Beam is splitted
                    map[y][x-1] = "|"
                    map[y][x+1] = "|"
                    # We have splitted 1 more time
                    total += 1
    
        render_map(map, "Total split: %d" % (total))
        time.sleep(0.2)
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))