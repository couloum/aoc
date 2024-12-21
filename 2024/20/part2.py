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
    for x in range(len(map)):
        for y in range(len(map[x])):
            if xy_to_s(x,y) in path:
                color = '\x1b[1;32;40m'
                print("%sO\x1b[0m" % (color), end="")
            elif xy_to_s(x,y) in explored:
                color = '\x1b[0;90;40m'
                print("%sO\x1b[0m" % (color), end="")
            else:
                print(map[x][y], end="")
        print("")


def print_explored_map2(map, cur, valid, invalid):
    output = ""
    for x in range(len(map)):
        for y in range(len(map[x])):
            if xy_to_s(x,y) == cur:
                output += "\x1b[1;31;40mx\x1b[0m"
            elif xy_to_s(x,y) in valid:
                output += "\x1b[1;32;40mx\x1b[0m"
            elif xy_to_s(x,y) in invalid:
                output += "\x1b[1;90;40mx\x1b[0m"
            else:
                output += map[x][y]
        output += "\n"
    print(output)
    
def find_shortest_path(map, graph, start, end):
    """
    Find shortest path using BFS algorithm
    """
    explored = []
    q = [[start]]

    while q:
        path = q.pop(0)
        node = path[-1]

        if node not in explored:
            neighbours = graph[node]

            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                q.append(new_path)
                if neighbour == end:
                    return new_path
                
            explored.append(node)
    

    return False

def build_graph(map):
    """
    Build a graph of nodes that can be used in a BFS algorithm
    Return a dictionary with every available positions and the associated neighbours
    """
    graph = dict()
    directions = ["-1,0", "0,-1", "1,0", "0,1"]
    for y in range(len(map)):
        for x in range(len(map)):
            if map[x][y] != "#":
                graph[xy_to_s(x,y)] = []
                # Explore neighbors
                for (dx,dy) in [s_to_xy(dir) for dir in directions]:
                    (nx,ny) = (x+dx,y+dy)
                    if nx < 0 or nx >= len(map) or ny < 0 or ny >= len(map):
                        continue
                    if map[x+dx][y+dy] != "#":
                        graph[xy_to_s(x,y)].append(xy_to_s(x+dx,y+dy))
    return graph

def find_shortcuts(map, path, min_save = 0):
    """
    From all points from the path, identify the distance between them.
    This distance must be at most 20, the number of cheat moves allowed
    Finally, we can filter out shortcuts that are not separated by enough distance (100)
    """

    shortcuts = []
    for i in range(len(path) - min_save - 1):
    #for i in range(3):
        valid = []
        invalid = []
        for j in range(i + min_save + 2, len(path)): 
            (x1,y1) = s_to_xy(path[i])
            (x2,y2) = s_to_xy(path[j])
            (dx,dy) = (abs(x2-x1), abs(y2-y1))

            distance = dx + dy

            time_save = j - (i + distance)

            # Ignore shortcuts that where distance is above allowed cheat moves
            if distance > 20:
                continue

            # Identify number of possible paths between the 2 points
            if time_save >= min_save:
                _log("Found a shortcut between (%d,%d) and (%d,%d) that saves %d picoseconds" % (x1,y1,x2,y2, time_save))
                valid.append(xy_to_s(x2,y2))
                shortcuts.append("%s,%s:%s,%s:%d" % (x1,y1,x2,y2,time_save))
            else:
                invalid.append(xy_to_s(x2,y2))

        if args.interactive: 
            os.system("clear")
            print_explored_map2(map, path[i], valid, invalid)
            print("i=%d" % (i))
            time.sleep(0.2)

    return shortcuts



def get_result(raw_data):
    """
    Build of graphs with all possible positions of the map
    Then use BFS algorithm to find the shortest path
    Finally, find all shortcuts that have a minimum distance of 100
    """
    total = 0

    map = read_data_map(raw_data)

    # Find start and end point
    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == "S":
                start_point = xy_to_s(x,y)
            elif map[x][y] == "E":
                end_point = xy_to_s(x,y)


    _log("Start point is (%s) and end point is (%s)" % (start_point, end_point))

    # Build graph of nodes and find shortest path using BFS algorithm
    graph = build_graph(map)
    _log("Graph of connections: %s" % (graph),3)

    shortest_path = find_shortest_path(map, graph, start_point, end_point)
    _log("Shortest path has %d moves" % (len(shortest_path) - 1))

    
    if re.match(r'sample.*', args.input_file):
        min_dist = 50
        print_explored_map(map, shortest_path, [])
    else:
        min_dist = 100

    # Now, find each points that are at a distance of 2 maximum
    shortcuts = find_shortcuts(map, shortest_path, min_dist)
    _log("Found %d shortcuts" % (len(shortcuts)))

    # Just for better debugging, display number of shortcuts per saved time
    shortcuts_dict = {}
    for shortcut in shortcuts:
        (p1,p2,t) = shortcut.split(":")
        if not t in shortcuts_dict:
            shortcuts_dict[t] = []
        
        shortcuts_dict[t].append(shortcut)
    
    for t in sorted(shortcuts_dict.keys()):
        _log("There are %-2d cheats that save %d picoseconds." % (len(shortcuts_dict[t]), int(t)))
        _log("%s" % (shortcuts_dict[t]), 2)

    total = len(shortcuts)

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))