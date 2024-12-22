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

# =============================================================================
# Puzzle code
# =============================================================================

#def read_data_custom(raw_data):
#    data = []
#
#    return data

def get_move(start,end,avoid):
    """
    Give the best sequence to go from one position to another
    Several things to consider to have the best sequence:
    - We should finish in priority with '^' or '>' as it is closer to 'A'. We should start with '<' as it's farest.
    - We must avoid the forbiden key
    - It's best to group the same movements. So, in order to avoid the forbiden key, we not respect the preference to finish by '>' or '^'
    """
    (sy,sx) = s_to_yx(start)
    (ey,ex) = s_to_yx(end)
    (dy,dx) = (ey-sy,ex-sx)
    (ay,ax) = s_to_yx(avoid)

    sequence = ""
    
    # Move left first, unless we hit the forbiden key
    # Then move down
    # Finally move up / right

    # Move left
    while dx < 0:
        if sy == ay and ex == ax:
            # Must move up/down to not hit forbiden key
            while dy < 0:
                sequence += '^'
                sy -= 1
                dy += 1
            while dy > 0:
                sequence += 'v'
                sy += 1
                dy -= 1
        sequence += '<'
        dx += 1
        sx -= 1
    
    # Then move down
    while dy > 0:
        # Must move right to not hit forbiden key (the forbiden key is always on the left)
        if sx == ax and ey == ay:
            while dx > 0:
                sequence += '>'
                dx -= 1
                sx += 1
        sequence += 'v'
        dy -= 1
        sy += 1
    
    # Finaly move right (no risk to hit the forbiden key)
    while dx > 0:
        sequence += '>'
        dx -= 1
        sx += 1

    # Then move up
    while dy < 0:
        # Must move right to not hit forbiden key (the forbiden key is always on the left)
        if sx == ax and ey == ay:
            while dx > 0:
                sequence += '>'
                dx -= 1
                sx += 1
        sequence += '^'
        dy += 1
        sy -= 1


    return sequence
    



def get_typing_sequence(code, keypad):
    """
    Apply a single keypad to a code, to get sequence of typing
    """

    keypad_map = keypad['map']
    keypad_coord = keypad['coord']


    # Find starting point: letter A
    cur_pos = keypad_coord['A']
    forbid_key_pos = keypad_coord[' ']

    final_sequence = ""
    for touch in code:
        next_pos = keypad_coord[touch]
        
        sequence = get_move(cur_pos, next_pos, keypad_coord[' '])
        
        # Push 'A' button at the end
        sequence += 'A'

        _log("Go to touch %s with sequence %s" % (touch, sequence), 3)

        # Change current position
        cur_pos = next_pos
        final_sequence += sequence

    return final_sequence
            
            
        

def get_final_sequence(code, keypads):
    """
    Apply all keypads to a specific code, to get the final sequence of typing
    """

    sequence = code
    i = 1
    for keypad in keypads:
        sequence = get_typing_sequence(sequence, keypad)
        _log("Sequence after keypad %d: %s" % (i, sequence), 2)
        i += 1

    return sequence

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
    #print_map(numeric_keypad['map'])
    #print_map(directional_keypad['map'])

    for keypad in [numeric_keypad, directional_keypad]:
        keypad['coord'] = {}
        for y in range(len(keypad['map'])):
            for x in range(len(keypad['map'][y])):
                touch = keypad['map'][y][x]
                keypad['coord'][touch] = yx_to_s(y,x)

    codes = raw_data.split("\n")

    keypads = [directional_keypad, directional_keypad, directional_keypad, directional_keypad, directional_keypad, directional_keypad, directional_keypad, directional_keypad]
    for code in ['>^^A', '^^>A']:
        _log("Calculating typing sequence for code %s" % (code), 2)
        sequence = get_final_sequence(code, keypads)

        # Calculate complexity
        #complexity = len(sequence) * int(code.rstrip('A'))
        _log("%s: %s" % (code, len(sequence)))

        #total += complexity



    return total
    
   
# Do not remove me

print_result(get_result(raw_data))