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

def part1(raw_data):
    sum = 0
    for line in raw_data.split("\n"):
        _log("Line: %s" % (line), 3)
        (card_number, line) = [ x.strip() for x in line.split(":") ]
        (winning_numbers, card_numbers) = [ x.strip() for x in line.split("|") ]
        winning_numbers = re.findall("\d+", winning_numbers)
        card_numbers = re.findall("\d+", card_numbers)
        _log("%s" % (card_number), 1)
        _log(" Winning numbers: %s" % (winning_numbers), 1)
        _log(" Card numbers: %s" % (card_numbers), 1)
        points = 0
        for num in card_numbers:
            if num in winning_numbers:
                points = max(1, 2 * points)
                _log("%s is a winning number! New card points: %s" % (num, points), 3)

        sum += points
        _log("This card points: %s - Total cards points: %s" % (points, sum))

    return sum



if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


result = 0


with open(args.input_file) as f:
    raw_data = f.read().strip()


result = part1(raw_data)
if args.verbose > 0: 
    print("\n================")
print("Result: %s" % (result))

        
        
