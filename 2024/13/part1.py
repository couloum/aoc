#!/usr/bin/env python3

import argparse
import re
import os
import sys
#import numpy as np
#import math

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

def xy_to_s(x, y):
    return "%d,%d" % (x,y)

def s_to_xy(xy):
    (x, y) = xy.split(",")
    return (int(x), int(y))

def in_map(map, x, y):
    """
    Tell if a given location is inside (True) or outside (False) of a given map (2D array)
    """
    if x < 0 or x >= len(map):
        return False
    if y < 0 or y >= len(map[x]):
        return False
    return True

def copy_map(map):
    """
    Create a copy of a map
    """
    new_map = []
    for x in range(len(map)):
        new_map.append(map[x].copy())
    return new_map

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

# =============================================================================
# Puzzle code
# =============================================================================

def read_data_custom(raw_data):
   data = []
   lines = raw_data.split("\n")
   re_button = re.compile(r"^Button [AB]: X\+([0-9]+), Y\+([0-9]+)")
   re_prize = re.compile(r"Prize: X=([0-9]+), Y=([0-9]+)")

   for i in range(0, len(lines), 4):
       (a_x, a_y) = re_button.fullmatch(lines[i]).group(1,2)
       (b_x, b_y) = re_button.fullmatch(lines[i+1]).group(1,2)
       (p_x, p_y) = re_prize.fullmatch(lines[i+2]).group(1,2)
       tmp = dict({
           "a": xy_to_s(int(a_x), int(a_y)),
           "b": xy_to_s(int(b_x), int(b_y)),
           "prize": xy_to_s(int(p_x), int(p_y)),
       })
       data.append(tmp)

   return data

def get_cheapest_win(machine):
    """
    Identify the minimal amount to win a price.
    Return that amount.
    If not possible to win, return 0.
    """

    # Get coordonates of the prize
    # + increments when pressing a/b buttons
    (px, py) = s_to_xy(machine["prize"])
    (dax, day) = s_to_xy(machine["a"])
    (dbx, dby) = s_to_xy(machine["b"])

    _log("Calculating winning combination for prize=(%d,%d) A=(+%d,+%d) B=(+%d,+%d)" % (px, py, dax, day, dbx, dby))
    # We know that we need less than 100 mouvements to win
    # Also, as B button cost only 1 token, we prefer to have the highest value possible for B
    for nb_a in range(1,101):
        for nb_b in range(1, 101):
            # Calculate current position and see if it matches the one from the prize
            if (nb_a * dax + nb_b * dbx) == px and (nb_a * day + nb_b * dby) == py:
                cost = 3 * nb_a + nb_b
                _log("[OK] Found a win with %d A and %d B. Cost=%d" % (nb_a, nb_b, cost))
                # The first match is the good match. Just return
                return cost
            
    # If we are here, then there is no match possible
    _log("[!!] No winning combination found")
    return 0


def get_result(raw_data):
    """
    
    """
    total = 0

    data = read_data_custom(raw_data)

    #_log("data=%s" % (data))

    for machine in data:
        total += get_cheapest_win(machine)
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))