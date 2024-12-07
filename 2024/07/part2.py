#!/usr/bin/env python3

import argparse
import re
import os
import sys
import numpy as np
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

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

# =============================================================================
# Puzzle code
# =============================================================================

# def read_data_custom(raw_data):
#    data = []
#    return data

def is_valid_operation(result, values, cur_result = 0):
    """
    Identify if we can get 'result' by summing or multiplying 'values' together.
    For part 2, add the new "||" operator which just concatenate values together
    (ie, 12||26 = 1226)
    Values must be kept in their curent order
    Operations are done from left to right (no sign precedence)
    This is a recursive function
    """

    _log("valid_operation(%d, %s, %d)" % (result, values, cur_result), 3)

    # Exit the recursion as soon as possible
    if len(values) == 0:
        return cur_result == result
    
    # Create a copy of values
    values2 = values.copy()

    # Get first element from values
    cur_val = values2[0]
    del(values2[0])

    # Try to add it and multiply it to cur_result
    # if cur_result is just 0, only sum
    if is_valid_operation(result, values2, cur_result + cur_val):
        return True
    
    if cur_result > 0:
        if is_valid_operation(result, values2, cur_result * cur_val):
            return True
        
        # Add new "||" operator
        if is_valid_operation(result, values2, int("%d%d" % (cur_result, cur_val))):
            return True
    
    return False

#
# Main function
#
def get_result(raw_data):
    """
    Just get inputs and pass them to is_valid_operation() function to see if numbers can
    be arranged to get the result. 
    """
    total = 0

    operations = raw_data.split("\n")
    for operation in operations:
        (result, tmp) = operation.split(":")
        result = int(result)
        tmp = tmp.strip()
        values = [int(x) for x in tmp.split(" ")]

        if is_valid_operation(result, values):
            _log("[OK] Operation with %s DO    have %d as result" % (values, result))
            total += result
        else:
            _log("[!!] Operation with %s DON'T have %d as result" % (values, result))

    return total
    
   

result = get_result(raw_data)
print_result(result)

        
        
