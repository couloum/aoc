#!/usr/bin/env python3

import argparse
import re
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, nargs='?', default="input.txt", help="Input file")
parser.add_argument('--verbose', '-v', action='count', default=0, help="Increase verbosity level")


args = parser.parse_args()

def _log(msg, level = 1):
    if level <= args.verbose:
        print("[DEBUG] %s" % (msg))

def print_map(map):
    for x in range(len(map)):
        for y in range(len(map[x])):
            print(map[x][y], end="")
        print("")

def is_part_num(map, row, col):
    _log("Testing special chars arround '%s' at position [%d][%d]" % (map[row][col], row, col), 2)
    for i in range(-1, 2):
        for y in range(-1, 2):
            _row = row + i
            _col = col + y
            if _row >= 0 and _row < len(map):
                if _col >= 0 and _col < len(map[_row]):
                    char = map[_row][_col]
                    _log("Found char '%s' at position [%d][%d]" % (char, _row, _col), 3)
                    if char == "." or char.isdigit():
                        continue
                    _log("%s is a special char at position [%d][%d]" % (char, _row, _col), 2)
                    return True
    _log("No special char found arround", 2)
    return False

def part1(map):
    sum = 0
    for row in range(len(map)):
        num = 0
        part_num_flag = False
        for col in range(len(map[row])):
            char = map[row][col]
            if char.isdigit():
                num *= 10
                num += int(char)
                if is_part_num(map, row, col):
                    part_num_flag = True
            elif num > 0:
                if part_num_flag:
                    _log("Found part number: %d" % (num), 1)
                    sum += num
                else:
                    _log("This number is not a part number: %d" % (num), 1)
                num = 0
                part_num_flag = False
        if num > 0:
            if part_num_flag:
                _log("Found part number: %d" % (num), 1)
                sum += num

    return sum

if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


result = 0


with open(args.input_file) as f:
    raw_data = f.read().strip()


#print(raw_data)

i = 0
map = []
for line in raw_data.split("\n"):
    map.append([c for c in line])

#print_map(map)
        
result = part1(map)
print("===========")
print("Result: %s" % (result))

        
        
