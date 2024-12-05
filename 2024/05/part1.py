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

def read_data_custom(raw_data):
    """
    Separates the page ordering rules from the updates within the input
    """
    data_all = raw_data.split("\n")

    data_rules = []
    data_updates = []
    for item in data_all:
        if "|" in item:
            data_rules.append(item)
        elif "," in item:
            data_updates.append(item)

    return (data_rules, data_updates)

def rules_cmp(data_rules, a, b):
    """
    Just compare 2 numbers togethers based on page ordering rules.
    return -1 if a < b
    return  1 if a > b
    Should never return 0
    """
    for rule in data_rules:
        (inf, sup) = rule.split("|")
        if (a == inf and b == sup):
            return -1
        if (a == sup and b == inf):
            return 1
    
    return 0


def sort_update(update, data_rules):
    """
    Custom sort function for update.
    Use page ordering rule to compare numbers
    Parse the array and just switch 2 numbers together if the 1st is > 2nd.
    Repeat until there is no change anymore.
    This is an unoptimized sort, but working.
    """

    change_flag = True
    while change_flag:
        change_flag = False
        for i in range(len(update) - 1):
            a = update[i]
            b = update[i+1]
            if rules_cmp(data_rules, a,b) > 0:
                update[i] = b
                update[i+1] = a
                change_flag = True

    return update

#
# Main function
#
def get_result(raw_data):
    """
    For each update, use a custom sort function that will use the page ordering rules to compare
    numbers between them
    """
    total = 0
    (data_rules, data_updates) = read_data_custom(raw_data)

    #For each update, sort it using custom sort function
    #If result after "sort" is same than before, then update is already in asc order
    for update in data_updates:
        update_arr = update.split(",")
        ordered_update = sort_update(update_arr.copy(), data_rules)
        _log("Update_arr: %s| ordered_update: %s" % (update_arr, ordered_update), 2)

        if update_arr == ordered_update:
            value = int(update_arr[int(len(update_arr)/2)]) # Get value from middle number
            total += value
            _log("[OK] %s is a valid update. add %d. Total=%d" % (update_arr, value, total))
        else:
            _log("[!!] %s is an invalid update" % (update_arr))

    return total
    
   

result = get_result(raw_data)
print_result(result)

        
        
