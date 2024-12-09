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

def print_result(result1, result2):
    if args.verbose > 0: 
        print("\n================")
    print("Result part 1: %s" % (result1))
    print("Result part 2: %s" % (result2))

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

#
# Main function
#
def get_results(raw_data):
    """
    
    """
    total1 = 0
    total2 = 0

    # Analyze string and put correct numbers for files and free spaces
    # The ID of files will be the ID inside "files" array
    inodes = dict({"free": []})
    filesystem = []
    fs_position = 0
    idx=0
    total_size = 0 # Total size of filesystem (size of files + size of free spaces)
    for num in raw_data:
        num = int(num)
        if idx % 2 == 0:
            file_id = (idx / 2)
            inodes[file_id] = ["%d:%d" % (fs_position, num)]
        else:
            file_id = -1
            inodes["free"].append("%d:%d" % (fs_position, num))

        
        for i in range(num):
            filesystem.append(file_id)

        total_size += num
        idx += 1

    _log("Filesystem is %d blocks" % (total_size))

    last_block_pos = len(filesystem) - 1

    for idx in range(len(filesystem)):
        # Fill free space with files that are in last positions
       if filesystem[idx] == -1:
            # Find last block not free
            while filesystem[last_block_pos] < 0:
                last_block_pos -= 1
            
            if idx >= last_block_pos:
                _log("Defragmentation finished at block %d" % (idx))
                break

            _log("Switching block %d (file_id: %d) with %d (free block)" % (last_block_pos, filesystem[last_block_pos], idx), 2)
            filesystem[idx] = filesystem[last_block_pos]
            filesystem[last_block_pos] = -1
    

    # Calculating checksum
    checksum = 0
    for idx in range(len(filesystem)):
        if filesystem[idx] < 0:
            continue
        checksum += idx * filesystem[idx]

    total1 = int(checksum)
    return (total1, total2)
    
   
# Do not remove me
(res1, res2) = get_results(raw_data)
print_result(res1, res2)