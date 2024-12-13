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
           "prize": xy_to_s(10000000000000+int(p_x), 10000000000000+int(p_y)),
           #"prize": xy_to_s(int(p_x), int(p_y)),
       })
       data.append(tmp)

   return data

def get_cheapest_win(machine):
    """
    Identify the minimal amount to win a price.
    Return that amount.
    If not possible to win, return 0.
    """

    # Notice that there's always a button that move more X than Y and vice-versa.
    # This means that if we want to reach the prize, we need to find the good ratio between X and Y increases

    # With this exemple:
    # Button A: X+94, Y+34
    # Button B: X+22, Y+67
    # Prize: X=8400, Y=5400

    # prize delta = 8400 - 5400 = 3000
    # So we need to have X to be exactly +3000 compared to Y to reach the prize
    # When pushing A, we increase X by +60 compared to Y
    # When pushing B, we decrease X by -45 compared to X

    # Which combination of +60 and -45 leads to +3000?
    # Let's call X = number of times we press button A and Y = number of times we press button B
    # We can write:
    # 1) X x 60 + Y x -45 = 3000
    # And how many press on button A and button B lead to reach prize X?
    # 2) X x 94 + Y x 22 = 8400
    #
    # Oh, wait a second, this is an equation with 2 unknowns that we have to solve
    #
    # Let's rewrite that a bit:
    # 1) Y = (3000 - X x 60) / -45
    #
    # 2) X x 94 + 22 x (3000 - X x 60) / -45 = 8400
    #    94 x -45 x X + 22 x 3000 - X x 22 x 60 = -45 x 8400
    #    94 x -45 x X - 22 x 60 x X = -45 x 8400 - 3000 x 22
    #    X x (94 x -45 - 22 x 60) = -45 x 8400 - 3000 x 22
    #    X = (-45 x 8400 - 3000 x 22) / (94 x -45 - 22 x 60)
    #    X = 80
    #
    # Now that we found X, let's calculate Y
    # 1) Y = (3000 - 80 x 60) / -45 = 40
    #
    # Transposing numbers into variables:
    # -   94 = xA = increment for X when pushing button A
    # -   22 = xB = increment for X when pushing button B
    # -   60 = dA = difference between xA and yA
    # -  -45 = dB = difference between xB and yB
    # - 8400 = xP = X position of prize
    # - 3000 = dP = diffference between xP and yP

    # So, we can write these 2 equations:
    #   - nbA = (dB * xP - dP * xB) / (xA * dB - xB * dA)
    #   - nbB = (dP - nbA * dA) / dB

    # Get all values we need
    (xP, yP) = s_to_xy(machine["prize"])
    (xA, yA) = s_to_xy(machine["a"])
    (xB, yB) = s_to_xy(machine["b"])
    dP = xP - yP
    dA = xA - yA
    dB = xB - yB

    _log("Calculating winning combination for prize=(%d,%d) A=(+%d,+%d) B=(+%d,+%d)" % (xP, yP, xA, yA, xB, yB))
    
    try:
        nb_a = (dB * xP - dP * xB) / (xA * dB - xB * dA)
        nb_b = (dP - nb_a * dA) / dB
        _log("nb_a=%f nb_b=%f" % (nb_a, nb_b), 2)
    except ZeroDivisionError:
        _log("[!!] No winning combination found")
        return 0

    # Ensure that result is not a floating number.
    # If result is floating number, then there's no possible result as we cannot press buttons less than 1 time.
    if (nb_a - int(nb_a)) != 0 or (nb_b - int(nb_b)) != 0:
        _log("[!!] No winning combination found")
        return 0

    # If we are here, then we have a valid solution
    cost = int(3 * nb_a + nb_b)
    _log("[OK] Found a win with %d A and %d B. Cost=%d" % (nb_a, nb_b, cost))
    return cost    


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