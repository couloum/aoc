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

def render_map(map, y, info):
    # Clear the screen and move the cursor to the top-left
    sys.stdout.write("\033[H\033[J")
    print(info)
    print("----------------------------------------------------------------------")
    output = ""

    y_min = max(y - 10, 0)
    y_max = min(y + 10, len(map))
    max_lines =  min(len(map), 20)
    if y_max - y_min < max_lines:
        if y_min == 0:
            y_max = max_lines
        else:
            y_min = y_max - max_lines
    for y in range(y_min, y_max):
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

    # General note:
    # Part2 is same as part one except that we will use numbers instead of "|" character
    # Everytime we see a splitter, we increase number on left and right (a "." is considered as 0)
    # At the end, we sum all numbers from last line to get the total

    # Replace "S" from 1st line with a 1 number
    i = map[0].index("S")
    map[0][i] = 1

    # Now, process line by line with this logic:
    # - If current pos is "^", add number above to direct left and right
    # - Else if above point is an integer
    #   - Add above number to current position ("." is considered as a 0)
    # 
    #
    # We assume this:
    # - There is always at least 1 "." between each "^" character
    # - There is not "^" character on the boarder of the map

    # Start parsing at line 1 (and not 0)
    for y in range(1, len(map)):
        for x in range (len(map[y])):
            if map[y][x] == "^":
                if type(map[y-1][x]) == int:
                    # Beam is splitted

                    # Replace "." with 0 on left and right
                    if  map[y][x-1] == ".":
                        map[y][x-1] = 0
                    if map[y][x+1] == ".":
                        map[y][x+1] = 0

                    # Increase number on left and right
                    map[y][x-1] += map[y-1][x]
                    map[y][x+1] += map[y-1][x]
                    total += 1
            elif type(map[y-1][x]) == int :
                if map[y][x] == ".":
                    map[y][x] = 0
                map[y][x] += map[y-1][x]
    
        #render_map(map, y, "Total split: %d" % (total))
        #time.sleep(1)

    # Now sum all numbers from last line
    total = 0
    y = len(map) - 1
    for x in range(len(map[y])):
        if type(map[y][x]) == int:
            total += map[y][x]
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))