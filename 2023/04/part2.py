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

def part2(raw_data):
    total = 0

    # Initialize all cards instances. At the moment 0 per card.
    card_instances = [ 0 for i in range(200)]
    card_idx = 1

    for line in raw_data.split("\n"):
        _log("Line: %s" % (line), 3)

        # Add 1 instance of the card we're just processing
        card_instances[card_idx] += 1

        (card_number, line) = [ x.strip() for x in line.split(":") ]
        card_number = re.findall("\d+", card_number)[0]
        (winning_numbers, card_numbers) = [ x.strip() for x in line.split("|") ]
        winning_numbers = re.findall("\d+", winning_numbers)
        card_numbers = re.findall("\d+", card_numbers)
        _log("Card number %s" % (card_number), 1)
        _log(" Winning numbers: %s" % (winning_numbers), 1)
        _log(" Card numbers: %s" % (card_numbers), 1)
        _log(" Instances of this card: %s" % (card_instances[card_idx]))
        for i in range(card_instances[card_idx]):
            points = 0
            for num in card_numbers:
                if num in winning_numbers:
                    points += 1
                    _log("%s is a winning number! New card points: %s" % (num, points), 3)
            for y in range(1, points + 1):
                if card_idx + y > 199:
                    break
                card_instances[card_idx+y] += 1
        
        _log(" This card points: %s" % (points))
        total = sum(card_instances)
        _log(" Total cards instances: %s" % (total))
        card_idx += 1

    
    return total



if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


result = 0


with open(args.input_file) as f:
    raw_data = f.read().strip()


result = part2(raw_data)
if args.verbose > 0: 
    print("\n================")
print("Result: %s" % (result))

        
        
