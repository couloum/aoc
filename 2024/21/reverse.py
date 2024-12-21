#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
import numpy as np
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
                output += map[x][y]
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

#def read_data_custom(raw_data):
#    data = []
#
#    return data

def get_code(sequence, keypad):
    """
    Apply a single keypad to a code, to get sequence of typing
    """

    keypad_map = keypad['map']
    keypad_coord = keypad['coord']

    # Find starting point: letter A
    cur_pos = keypad_coord['A']

    directions = {
        '<': (0,-1),
        '>': (0,1),
        '^': (-1,0),
        'v': (1,0),
        'A': (0,0),
    }

    code = ""
    (cx, cy) = s_to_xy(cur_pos)
    seq = ""
    for touch in sequence:
        seq += touch
        if touch == 'A':
            tmp = keypad_map[cx][cy]
            code += tmp
            _log("Press touch %s after sequence %s" % (tmp, seq), 3)
            seq = ""
        else:
            dxy = directions[touch]
            (cx,cy) = (cx+dxy[0], cy+dxy[1])

    return code
            
            
        

def get_final_code(sequence, keypads):
    """
    Apply all keypads to a specific code, to get the final sequence of typing
    """

    code = sequence
    i = 1
    for keypad in keypads:
        code = get_code(code, keypad)
        _log("Code after keypad %s: %s" % (i, code), 2)
        i += 1

    return code

def get_result(raw_data):
    """
    
    """
    total = 0

    numeric_keypad = {
        'map': [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            [' ', '0', 'A'],
        ]
    }
    directional_keypad = {
        'map': [
            [' ', '^', 'A'],
            ['<', 'v', '>'],
        ]
    }

    for keypad in [numeric_keypad, directional_keypad]:
        keypad['coord'] = {}
        for x in range(len(keypad['map'])):
            for y in range(len(keypad['map'][x])):
                touch = keypad['map'][x][y]
                keypad['coord'][touch] = xy_to_s(x,y)

    sequences = [
        '<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A',
        '<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A',
        '<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A',
        '<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A',
        '<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A',
    ]

    keypads = [directional_keypad, directional_keypad, numeric_keypad]
    for sequence in sequences:
        _log("Calculating reverse code for sequence %s" % (sequence), 2)
        code = get_final_code(sequence, keypads)



    return total
    
   
# Do not remove me

print_result(get_result(raw_data))