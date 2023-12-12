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

def read_data(raw_data):
    races = []
    (raw_times, raw_distances) = raw_data.strip().split("\n")
    times = ["".join(raw_times.split(" ")).split(":")[1]]
    distances = ["".join(raw_distances.split(" ")).split(":")[1]]
    _log("times=%s / distances=%s" % (times, distances), 3)
    for idx in range(len(times)):
        races.append((times[idx], distances[idx]))

    return races

#def enrich_maps(maps):
#    for idx, m in enumerate(maps):
#        for item in m:
#            (dest, source, num) = item
#            map_idx = []
#            for i in range(source, num):

def part2(raw_data):
    total = 1
    races = read_data(raw_data)
    _log("Races: %s" % (races))
   
    for race in races:
        _time = int(race[0])
        _min_dist = int(race[1])
        _win_combinations = 0
        _log("Computing race with time=%d and dist=%d" % (_time, _min_dist))
        for i in range(_time+1):
            _dist = i*(_time - i)
            if _dist > _min_dist:
                _log("Winning combination: hold %d ms -> dist=%d" % (i, _dist), 2)
                _win_combinations += 1
        total *= _win_combinations
        _log("Found %d winning combinations. Total so far: %d" % (_win_combinations, total))

    return total
    



if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


with open(args.input_file) as f:
    raw_data = f.read().strip()


result = part2(raw_data)
if args.verbose > 0: 
    print("\n================")
print("Result: %s" % (result))

        
        
