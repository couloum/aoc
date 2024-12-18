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
    if level <= args.verbose:
        for y in range(len(map)):
            for x in range(len(map[y])):
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

#def read_data_custom(raw_data):
#    data = []
#
#    return data

def print_explored_map(map, path, explored):
    for y in range(len(map)):
        for x in range(len(map)):
            if xy_to_s(x,y) in path:
                color = '\x1b[1;32;40m'
                print("%sO\x1b[0m" % (color), end="")
            elif xy_to_s(x,y) in explored:
                color = '\x1b[0;90;40m'
                print("%sO\x1b[0m" % (color), end="")
            else:
                print(map[x][y], end="")
        print("")
    
def find_shortest_path(map, graph, start, end):
    """
    Find shortest path using BFS algorithm
    """
    explored = []
    q = [[start]]

    while q:
        path = q.pop(0)
        node = path[-1]

        if args.interactive:
            os.system("clear")
            print_explored_map(map, path, explored)
            time.sleep(0.1)

        if node not in explored:
            neighbours = graph[node]

            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                q.append(new_path)

                if neighbour == end:
                    # Remove the start node so it doesn't count in path length
                    new_path.pop(0)
                    return new_path
                
            explored.append(node)
    

    return []

def build_graph(map):
    """
    Build a graph of nodes that can be used in a BFS algorithm
    Return a dictionary with every available positions and the associated neighbours
    """
    graph = dict()
    directions = ["-1,0", "0,-1", "1,0", "0,1"]
    for y in range(len(map)):
        for x in range(len(map)):
            if map[x][y] == ".":
                graph[xy_to_s(x,y)] = []
                # Explore neighbors
                for (dx,dy) in [s_to_xy(dir) for dir in directions]:
                    (nx,ny) = (x+dx,y+dy)
                    if nx < 0 or nx >= len(map) or ny < 0 or ny >= len(map):
                        continue
                    if map[x+dx][y+dy] == ".":
                        graph[xy_to_s(x,y)].append(xy_to_s(x+dx,y+dy))
    return graph


def get_result(raw_data):
    """
    Try all possibles maps with memory corruption.
    Start with all possible positions corrupted and test if there is a path, using code from part 1.
    If no path, try the map by removing the latest corrupted memory block (actually, the map is entirely rebuilt).
    Do that until one path is found.
    """
    total = 0

    bytes_coord = raw_data.split("\n")

    if re.match(r'sample.*', args.input_file):
        map = np.full((7,7), '.')
        min_size = 12
        end = "6,6"
    else:
        map = np.full((71,71), '.')
        min_size = 1024
        end = "70,70"
   
    # Find a point near the middle of the map that never get corrupted
    mid_point = None
    for i in range(int(len(map)/2)):
        x = len(map)/2 + i
        y = x
        for (dx,dy) in [(0,0), (-1,0), (0,-1), (1,0), (0,1)]:
            if not xy_to_s(x+dx,y+dy) in bytes_coord:
                mid_point = xy_to_s(x+dx,y+dy)
                break
        if mid_point:
            break
    
    # Instead of checking paths working untill one doesn't work, check paths not working until one works
    for size in range(len(bytes_coord)-1, 0, -1):
    #for size in range(2463, 0, -1):
        _log("Testing with %dth corrupted memory on position %s" % (size, bytes_coord[size-1]))
        # Build the map
        new_map = map.copy()
        for (x,y) in [s_to_xy(x) for x in bytes_coord[0:size]]:
            new_map[x][y] = "#"

        #print_map(new_map)
        # Calculate graph
        graph = build_graph(new_map)
        #_log("Graph of connections: %s" % (graph),3)

        # Instead of checking shortest path between start and end, compute shortest path
        # between start and middle point + between middle point and end
        path = find_shortest_path(new_map, graph, "0,0", end)
        if len(path) == 0:
            continue

        print_explored_map(new_map, path, [])
        total = bytes_coord[size]
        _log("One path found")
        break

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))