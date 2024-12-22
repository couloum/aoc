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

def get_cost_digital_keypad(touch, iterations):
    single_cost = {
        '<': 'v<<A',
        '^': '<A',
        '>': 'vA',
        'v': '<vA',
        'A': 'A',
    }
    cost = 0
    if iterations == 0:
        return 1
    for t in single_cost[touch]:
        cost += get_cost_digital_keypad(t, iterations-1)
    return cost

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

    # Few tricks for keypad type 2
    if avoid == "0,0":
        if dx == 1 and dy == -1 and sx > 0:
            return '^>'

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
    

global chunks_cache_single
global chunks_cache_all
chunks_cache_single = {}
chunks_cache_all = {}

def get_typing_sequence(code, keypad, use_cache = False):
    """
    Apply a single keypad to a code, to get sequence of typing
    """

    global chunks_cache_single

    keypad_map = keypad['map']
    keypad_coord = keypad['coord']


    # Find starting point: letter A
    cur_pos = keypad_coord['A']
    forbid_key_pos = keypad_coord[' ']

    # Identify all chunk of code separated by a 'A'
    code_chunks = ["%sA" % (x) for x in code.split('A')[0:-1]]

    final_sequence = ""
    for code_chunk in code_chunks:
        _log("Get typing sequence for chunk %s" % (code_chunk), 4)

        # See if this chunk is in cache first
        if use_cache:
            if code_chunk in chunks_cache_single:
                tmp = chunks_cache_single[code_chunk]
                _log("Result found in cache for code chunk %s: %s" % (code_chunk, tmp), 4)
                final_sequence += tmp
                # As we finish by a A, don't need to change cur_pos
                continue

        # If not, calculate it
        sequence = ""
        for touch in code_chunk:
            next_pos = keypad_coord[touch]
            tmp = get_move(cur_pos, next_pos, keypad_coord[' '])
            
            # Push 'A' button at the end
            tmp += 'A'

            _log("Go to touch %s with sequence %s" % (touch, tmp), 4)
            sequence += tmp

            # Change current position
            cur_pos = next_pos
        _log("Calculated sequence for code chunk %s: %s" % (code_chunk, sequence), 4)
        
        if use_cache:
            chunks_cache_single[code_chunk] = sequence
        final_sequence += sequence

    return final_sequence
            
            
def sum_chunks(base_chunks, new_chunks, multiplier):
    """
    Add new_chunks into base_chunks. Apply a multiplier to all new chunks
    """

    _log("sum_chunks(base_chunks=%s, new_chunks=%s, multiplier=%d)" % (base_chunks, new_chunks, multiplier), 4)

    for (chunk, nb) in new_chunks.items():
        if not chunk in base_chunks:
            base_chunks[chunk] = 0
        base_chunks[chunk] += nb * multiplier
    _log("base_chunks=%s" % (base_chunks), 4)

def sub_chunks(base_chunks, sub_chunks):
    for (chunk, nb) in sub_chunks.items():
        base_chunks[chunk] -= nb 
    if base_chunks[chunk] == 0:
        del(base_chunks[chunk])


def transform_chunks(chunks, keypad, iterations, use_cache=True):
    """
    Apply specified keypad multiple times
    Return a dictionary with chunks and number of time they appear
    """

    _log("transform_chunks(chunks=%s, keypad, iterations=%d, use_cache=%s)" % (chunks, iterations, use_cache), 3)

    global chunks_cache_all

    result_chunks = chunks

    for iteration in range(iterations):
        working_chunks = result_chunks.copy()
        for (chunk, chunk_nb) in working_chunks.items():
            if chunk_nb == 0:
                continue

            _log("[iter=%d] Calculating sequence for chunk {%s: %d}" % (iteration, chunk, chunk_nb), 2)

            # Try to use cache
            if use_cache and chunk in chunks_cache_all:
                new_chunks = chunks_cache_all[chunk]
                _log("Chunk found in cache: {%s: %d} -> %s" % (chunk, chunk_nb, new_chunks), 3)
            else:

                # If not in cache, compute
                new_chunks = {}
                tmp = get_typing_sequence(chunk, keypad, use_cache)
        
                for ch in ["%sA" % (x) for x in tmp.split('A')[0:-1]]:
                    if not ch in new_chunks:
                        new_chunks[ch] = 1
                    else:
                        new_chunks[ch] += 1
                
                if use_cache:
                    chunks_cache_all[chunk] = new_chunks

                _log("Sequence for code chunk %s calculated: %s" % (chunk, new_chunks), 3)
            
            sub_chunks(result_chunks, {chunk: chunk_nb})
            sum_chunks(result_chunks, new_chunks, chunk_nb)

        _log("Chunks after iteration #%d: %s" % (iteration, result_chunks))
    
    _log("Cache: %s" % (chunks_cache_all))
    return result_chunks

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

    for code in codes:
        _log("Calculating typing sequence for code %s" % (code), 2)
        chunks = transform_chunks({code: 1}, numeric_keypad, 1, False)
        #chunks = {'<A': 1, '^A': 1, '>^^A': 1, 'vvvA': 1}
        chunks = transform_chunks(chunks, directional_keypad, 25)
        #chunks = transform_chunks(chunks, directional_keypad, 24)

        length = 0
        for (chunk, nb) in chunks.items():
            length += len(chunk) * nb


        _log("Identified chunks for code %s: %s" % (code, chunks))
        _log("Length for this sequence: %d" % (length))

        # Calculate complexity
        complexity = length * int(code.rstrip('A'))
        _log("Found sequence for code %s, with complexity %d" % (code, complexity))

        total += complexity



    return total
    
   
# Do not remove me

print_result(get_result(raw_data))