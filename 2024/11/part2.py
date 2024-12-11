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

# def read_data_custom(raw_data):
#    data = []
#    return data

def get_next_stones(digit, iterations):
    if iterations == 0:
        return [digit]
    
    if digit == 0:
        return get_next_stones(1, iterations - 1)
    elif len(str(digit)) % 2 == 0:
        half = int(len(str(digit)) / 2)
        digit1 = int(str(digit)[0:half])
        digit2 = int(str(digit)[half:])
        return get_next_stones(digit1, iterations - 1) + get_next_stones(digit2, iterations - 1)
    else:
        return get_next_stones(digit * 2024, iterations - 1)
    

global stones_dict
stones_dict = dict()

def get_nb_stones(digit, blinks):
    _log("get_nb_stones(%d, %d)" % (digit, blinks), 3)
    global stones_dict

    nb_stones = 1
    for blink in range(blinks):
        if digit in stones_dict:
            new_digits = stones_dict[digit]
        else:
            new_digits = get_next_stones(digit)
        
        digit = new_digits[0]
        nb_stones += 1
        if len(new_digits) > 1:
            nb_stones += get_nb_stones(new_digits[1], blinks - 1)

    return nb_stones

def digits_array_to_dict(digits_array, factor=1):
    """
    Transform an array of numbers into a dictionnary where key is a number
    and value is the number of time this number appear.
    """
    digits_dict = dict()
    for digit in digits_array:
        if digit in digits_dict:
            digits_dict[digit] += factor
        else:
            digits_dict[digit] = factor
    return digits_dict

def digits_dict_sum(digits_dict1, digits_dict2):
    """
    Merge 2 dictionaries containing numbers as value.
    If keys are same, sum values
    If keys are new, just merge
    """
    digits_dict_sum = digits_dict1.copy()
    for (digit, nb) in digits_dict2.items():
        if digit in digits_dict_sum:
            digits_dict_sum[digit] += nb
        else:
            digits_dict_sum[digit] = nb
    return digits_dict_sum

def get_result(raw_data):
    """
    Use a dictionary to store stone numbers and number of stones with that number.
    Keep a cache of "from a given stone number, what number of stones do we get after"
    """
    total = 0

    data = [int(x) for x in raw_data.split(" ")]

    nb_iterations = 15
    step = 5
    
    digits = digits_array_to_dict(data)

    round = 1
    for iteration in range(1, nb_iterations+1):
        _log("Starting iteration #%d" % (iteration))
        nb_cache = 0
        nb_non_cache = 0
        new_digits = dict()
        _log("digits=%s" % (digits), 3)
        for (digit, nb) in digits.items():
            _log("Calculating with digit %d" % (digit), 2)
            if digit in stones_dict:
                tmp_digits = stones_dict[digit]
                nb_cache += 1
            else:
                tmp_digits = get_next_stones(digit, step)
                stones_dict[digit] = tmp_digits.copy()
                nb_non_cache += 1

            new_digits = digits_dict_sum(new_digits, digits_array_to_dict(tmp_digits, nb))
            _log("Digit %d: found %d stones after %d iterations." % (digit, nb * len(tmp_digits), step), 2)
        
        digits = new_digits
        round += 1
        _log("Iteration finished with %d from cache / %d from non cache" % (nb_cache, nb_non_cache))
        _log("%d stones at the end of the iteration, grouped in %d uniques digits" % (sum(digits.values()), len(digits.keys())))
    
    _log("digits=%s" % (digits), 3)

    total = sum(digits.values())

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))