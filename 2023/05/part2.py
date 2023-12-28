#!/usr/bin/env python3

import argparse
import re
import os
import sys
import numpy as np
import math

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

def print_result(result):
    if args.verbose > 0: 
        print("\n================")
    print("Result: %s" % (result))

if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


with open(args.input_file) as f:
    raw_data = f.read().strip()

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

# =============================================================================
# Puzzle code
# =============================================================================

# Global variables:
seeds = {}
maps = []
rmaps = []

def read_data_custom(raw_data):
    #data = []

    tmp = [int(x) for x in raw_data.split("\n")[0].split(":")[1].strip().split(" ")]
    for i in range(0, len(tmp), 2):
        seeds[tmp[i]] = tmp[i+1]
        
    map_idx = -1
    for line in raw_data.split("\n")[2:]:
        if re.match("^[-a-z]+ map:", line):
            map_idx += 1
            maps.append({})
            rmaps.append({})
        elif re.match("^\d+ \d+ \d+", line):
            (after, before, length) = line.split(" ")
            maps[map_idx][int(before)] = { "dst": int(after), "length": int(length) }
            rmaps[map_idx][int(after)] = { "dst": int(before), "length": int(length)}



def get_seed_and_location_values(val, map_id):
    """
    From any given value,
    from any given map,
    Calculate the seed value and the location value
    """

    # Get location value
    # Apply maps from current to latest
    location = val
    for i in range(map_id, len(maps)):
        _map = maps[i]
        for key in _map.keys():
            (start, end) = (key, key + _map[key]["length"] - 1)
            if location >= start and location <= end:
                _log("[location / %d #%d] found value %d in range %d->%d" % (val, i, location, start, end), 2)
                #match_keys.append(start)
                delta = key - _map[key]["dst"]
                _log("%d #%d. %d - %d -> %d" % (val, i, location, delta, location - delta), 2)
                location -= delta
                break
    
    # Get seed value
    # Apply reverse maps from previous to 1st
    seed = val
    for i in range(map_id-1, -1, -1):
        _map = rmaps[i]
        for key in _map.keys():
            (start, end) = (key, key + _map[key]["length"] - 1)
            if seed >= start and seed <= end:
                _log("[seed / %d #%d] found value %d in range %d->%d" % (val, i, seed, start, end), 2)
                #match_keys.append(start)
                delta = key - _map[key]["dst"]
                _log("%d #%d. %d - %d -> %d" % (val, i, seed, delta, seed - delta), 2)
                seed -= delta
                break

    _log("Value %d in map_id %d will translare into (seed=%d, location=%d)" % (val, map_id, seed, location))

    return (seed, location)


#
# Main function
#
def get_result(raw_data):
    total = 0
    read_data_custom(raw_data)

    _log("seeds: %s" % (seeds))
    _log("Map: %s" % (maps))
    _log("Reverse maps: %s" % (rmaps))


    # For each value in each map, get the corresponding seed and location values.
    # Register this into a map of locations to seeds.
    locations = {}
    map_idx = 0
    for _map in maps:
        _log("Processing map #%d" % map_idx)
        for val in _map.keys():
            (seed, location) = get_seed_and_location_values(val, map_idx)
            locations[location] = seed
            (seed, location) = get_seed_and_location_values(val + _map[val]["length"] - 1, map_idx)
            locations[location] = seed
        map_idx += 1
    
    # Now that we have a map of all possible boundaries of locations, process them in sorted order.
    # For each location boundary, identify corresponding seeds boundaries.
    # For each seed, identify if it belong into these boundaries
    _log("Locations map: %s" % (locations))
    loc_keys = sorted(locations.keys())
    for i in range(len(loc_keys) - 1):
        loc_start = loc_keys[i]
        loc_end = loc_keys[i+1] - 1
        loc_delta = loc_end - loc_start

        seed_start = locations[loc_start]
        seed_end = seed_start + loc_delta
        _log("Location %d -> %d (seeds %d -> %d)" % (loc_start, loc_end, seed_start, seed_end))

        for (seed_first, seed_last) in seeds.items():
            seed_last += seed_first - 1
            _log("  Searching in seeds %d -> %d" % (seed_first, seed_last))
            if seed_last < seed_start or seed_first > seed_start:
                continue
    
            seed_match = max([seed_start, seed_first])

            seed_delta = seed_match - seed_start
            loc_match = loc_start + seed_delta

            _log("Found seed %d being the 1st to match. Location = %d" % (seed_match, loc_match))
            return loc_match
        

    # Should not arrive here
    return int(total)


result = get_result(raw_data)
print_result(result)

        
        
