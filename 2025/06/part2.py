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
    raw_data = f.read()

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

def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    _log(_c(" === Read input ===", "green", bold=True))
    
    # For part 2, the way to read input is different, but then the logic to
    # calculate is the same.

    # For each line, we'll save in a table each caracter
    lines_char = []
    for line in raw_data.split("\n"):
        # Add a space at the end of the line for easier calculation later (will be our end)
        line = "%s " % (line)
        lines_char.append(list(line))

    print(lines_char)

    # List line is actually symbols
    # Remove every empty chars from it
    symbols = [s for s in lines_char.pop() if s != " "]

    # Now, get all digits
    items = []
    digits = []
    for i in range(len(lines_char[0])):
        digit = ""
        for line in lines_char:
            if line[i] != " ":
                digit = "%s%s" % (digit, line[i])
        if digit != "":
            digits.append(int(digit))
            _log("Found digit %s" % (digit), 3)
        else:
            items.append(digits.copy())
            _log("Adding list of digits to item: %s" % (digits))
            digits = []

    _log("Found lines of digits:")
    for i in range(len(items)):
        _log(" - %s" % (items[i]))
    _log("Found symbols:")
    _log(" - %s" % (symbols))

    _log("")
    _log(_c(" === Calculate ===", "green", bold=True))
    for i in range(len(symbols)):
        symbol = symbols[i]
        digits = items[i]
        if symbol == "+":
            answer = sum(digits)
        else:
            answer = math.prod(digits)
        _log("Calculating %s = %d" % (symbol.join([str(x) for x in digits]), answer))
        total += answer

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))