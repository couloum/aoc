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
parser.add_argument('--part1', '-1', action='store_true', default=False, help="Execute only part1")
parser.add_argument('--part2', '-2', action='store_true', default=False, help="Execute only part2")


args = parser.parse_args()
if not args.part1 and not args.part2:
    args.part1 = True
    args.part2 = True

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
    if args.part1:
        print("Result part 1: %s" % (result1))
    if args.part2:
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

def get_filesystem(raw_data):
    """
    Initialiaze the filesystem from raw data
    Filesystem is an array of blocks
    Each block can be free (ie, have no data). In that case, it contains value -1
    If block contains part of a file, it's value will be the file ID

    Filesystem is initialized from a "disk map" which is a string which alternative information on files and free space
    So, a disk map like "12345" would represent a one-block file, two blocks of free space, a three-block file, four blocks
    of free space, and then a five-block file. A disk map like 90909 would represent three nine-block files in a row
    (with no free space between them).
    Using one character for each block where digits are the file ID and . is free space, the disk map "12345" represents
    these individual blocks:
    0..111....22222
    It will be represented as-is in filesystem array:
    [0, -1, -1, 1, 1, 1, -1, -1, -1, -1, 2, 2, 2, 2, 2]
    """
    filesystem = []
    idx=0
    for num in raw_data:
        num = int(num)
        if idx % 2 == 0:
            file_id = int(idx / 2)
        else:
            file_id = -1

        for i in range(num):
            filesystem.append(file_id)

        idx += 1

    return filesystem

def get_last_position(filesystem_local, last_block_pos = -1):
    """
    Return position of last block from filesystem containing data
    """
    if last_block_pos == -1:
        last_block_pos = len(filesystem_local) - 1
    while filesystem_local[last_block_pos] < 0:
        last_block_pos -= 1
    return last_block_pos

def get_last_file(filesystem_local, last_block_pos = -1):
    """
    From last file in filesystem, return:
    - file ID
    - start position
    - size (in blocks)
    Optional: start searching from a specific position at the end (position -1, means the last block)
    """
    last_block_pos = get_last_position(filesystem_local, last_block_pos)
    size = 1
    if last_block_pos == 0:
        return (filesystem_local[last_block_pos], last_block_pos, size)
    
    while filesystem_local[last_block_pos-1] == filesystem_local[last_block_pos]:
        last_block_pos -= 1
        size += 1
    
    return (filesystem_local[last_block_pos], last_block_pos, size)

def get_first_free(filesystem_local, min_size = 0):
    """
    From first free blocks in filesystem, return:
    - start position
    - size (in blocks)
    Optional: specify a minimum size of free blocks. If none found, return -1 and -1
    """
    idx = 0
    while idx <len(filesystem_local):
        if filesystem_local[idx] < 0:
            start_pos = idx
            while idx < len(filesystem_local) and filesystem_local[idx] < 0:
                idx += 1
            size = idx - start_pos
            if size >= min_size:
                break
        idx += 1
    
    # If we reached the end of filesystem, return -1 (no free block found)
    if idx == len(filesystem_local):
        return (-1, -1)
    
    return (start_pos, size)


def get_checksum(filesystem_local):
    """
    Calculating checksum
    To calculate the checksum, add up the result of multiplying each of filesystem blocks' position with the file ID number
    it contains. The leftmost block is in position 0. If a block contains free space, skip it instead.
    With filesystem [0, 0, 9, 9, 8], the first few blocks' position multiplied by its file ID number are
    0 * 0 = 0, 1 * 0 = 0, 2 * 9 = 18, 3 * 9 = 27, 4 * 8 = 32.
    In this example, the checksum is the sum of these, 77.
    """
    checksum = 0
    for idx in range(len(filesystem_local)):
        if filesystem_local[idx] < 0:
            continue
        checksum += idx * filesystem_local[idx]

    return int(checksum)


#
# Main function
#

def init(raw_data):
    """
    Create the filesystem. Shared for part1 and part 2
    """
    # Define global variables
    global filesystem

    filesystem = get_filesystem(raw_data)

    _log("Filesystem is %d blocks" % (len(filesystem)))

def get_result1(raw_data):
    """
    Apply defragmentation algorithm defined in part1 and then calculate checksum
    """
    global filesystem
    total = 0

    filesystem_local = filesystem.copy()

    # Defragmentation, with algorithm 2

    
    for idx in range(len(filesystem_local)):
        # Fill free space with files that are in last positions
        last_block_pos = len(filesystem_local) - 1
        if filesystem[idx] == -1:
            # Find last block not free
            #last_block_pos = get_last_position(filesystem_local, last_block_pos)
            while filesystem_local[last_block_pos] < 0:
                last_block_pos -= 1
            
            if idx >= last_block_pos:
                _log("Defragmentation finished at block %d" % (idx))
                break

            _log("Switching block %d (file_id: %d) with %d (free block)" % (last_block_pos, filesystem_local[last_block_pos], idx), 2)
            filesystem_local[idx] = filesystem_local[last_block_pos]
            filesystem_local[last_block_pos] = -1
    

    total = get_checksum(filesystem_local)
    return total
    

def get_result2(raw_data):
    global filesystem
    total = 0

    filesystem_local = filesystem.copy()
    # Defragmentation, with algorithm 2

    ff_pos = 0
    lb_pos = 0
    while True:
        # Get last block (lb)
        (lb_file_id, lb_pos, lb_size) = get_last_file(filesystem_local, lb_pos - 1)
        _log("lb_file_id=%d lb_pos=%d lb_size=%d" % (lb_file_id, lb_pos, lb_size), 3)

        if lb_pos == 0:
            _log("Defragmentation finished at block %d" % (lb_pos))
            break

        # Get first free space (ff)
        (ff_pos, ff_size) = get_first_free(filesystem_local, lb_size)
        _log("ff_pos=%d ff_size=%d" % (ff_pos, ff_size), 3)

        if ff_pos == -1 or ff_pos > lb_pos:
            _log("[!!] File id %d: No free block with size %d found" % (lb_file_id, lb_size))
            continue
        
        _log("[OK] File ID %d: switch with size %d from block %d to block %d (%d blocks free)" % (lb_file_id, lb_size, lb_pos, ff_pos, ff_size))
        
        for i in range(lb_size):
            filesystem_local[ff_pos + i] = lb_file_id
            filesystem_local[lb_pos + i] = -1

        #_log(filesystem_local, 3)

    total = get_checksum(filesystem_local)

    return total
   
# Do not remove me
init(raw_data)
(result1, result2) = (0,0)
if args.part1:
    result1 = get_result1(raw_data)
if args.part2:
    result2 = get_result2(raw_data)
print_result(result1, result2)