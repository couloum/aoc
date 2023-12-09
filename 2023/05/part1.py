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

def read_data(raw_data):
    data = raw_data.split("\n")
    map_idx = -1
    maps = [ [] for i in range(7) ]
    seeds = [1]
    for line in data:
        line.strip()
        if line.startswith("seeds:"):
            _log("Found line for seeds: %s" % (line), 2)
            seeds = [ int(s) for s in re.findall("\d+", line) ]
            _log("seeds=%s" % (seeds), 2)
        elif line.endswith("map:"):
            map_idx += 1
            _log("Found line for map. New map idx=%d" % (map_idx), 3)
        elif line == "":
            pass
        else:
            maps[map_idx].append([int(l) for l in line.split(" ")])

    return (seeds, maps)

#def enrich_maps(maps):
#    for idx, m in enumerate(maps):
#        for item in m:
#            (dest, source, num) = item
#            map_idx = []
#            for i in range(source, num):

def part1(raw_data):
    total = 0
    (seeds, maps) = read_data(raw_data)
    _log("Seeds: %s" % (seeds))
    _log("List of maps:")
    for i, m in enumerate(maps):
        _log(" #%d: %s" % (i,m))

    locations = []

    for seed_idx, seed in enumerate(seeds):
        _log("processing seed #%d: %d" % (seed_idx, seed))
        _input = seed
        for map_idx, m in enumerate(maps):
            _log("|-> Processing map #%d" % (map_idx))
            _log("|   |-> Looking for translation %d in map" % (_input), 2)
            _output = _input
            for item in m:
                (dest, source, map_range) = item
                if _input in range(source, source + map_range):
                    _log("|   |-> Found input %d in map %s" % (_input, item), 2)
                    _output = _input + (dest - source)
                    break
            _log("|   L-> Input %d translate into %d" % (_input, _output))
            _input = _output

        _log("|-> Location for seed #%d: %d" % (seed_idx, _output))
        locations.append(_output)

    return min(locations)
    



if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


with open(args.input_file) as f:
    raw_data = f.read().strip()


result = part1(raw_data)
if args.verbose > 0: 
    print("\n================")
print("Result: %s" % (result))

        
        
