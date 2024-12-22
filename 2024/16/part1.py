#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
import numpy as np
#import math

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

class Path:
    """
    A class to explore a path in a map
    Each path is an instance of this class
    Only the map is shared between all instances
    """

    dir_dict = {
        '>': '0,1',
        'v': '1,0',
        '<': '0,-1',
        '^': '-1,0',
    }
    dir_array = ['>', 'v', '<', '^']

    def __init__(self, position, direction = '>', explored = [], points = 0):
        self.position = position
        (self.x,self.y) = s_to_xy(position)
        self.direction = direction
        self.explored = explored.copy()
        self.points = points
        self.is_dead = False

    def __str__(self):
        return "[Path(pos=(%s),dir='%s',explored=%d,points=%d)]" % (self.position, self.direction, len(self.explored), self.points)

    @classmethod
    def set_map(cls,map):
        cls.map = copy_map(map)

    def get_available_directions(self):
        """
        From a given positions, return of directions where we can go, if possible:
        -1 on the left
         0 straight
         1 on the right
         If we're already at the end, return no possible position.
         If no possible position and we're not at the end, consider the path as dead
        """

        if self.is_on_end():
            return []
        
        dir_idx = Path.dir_array.index(self.direction)
        available_directions = []
        for i in [0,-1,1]:
            #_log("dir_idx+i%%4 = %d+%d%%4=%d on %s" % (dir_idx, i, (dir_idx+i)%4, Path.dir_array),3)
            new_dir = Path.dir_array[(dir_idx+i)%4]
            (dx,dy) = s_to_xy(Path.dir_dict[new_dir])
            if Path.map[self.x+dx][self.y+dy] != "#" and not xy_to_s(self.x+dx,self.y+dy) in self.explored:
                #_log("Path %s: Append direction %d that will go on position (%d,%d) where map=%s" % (self, i, self.x+dx, self.y+dy, Path.map[self.x+dx][self.y+dy]))
                available_directions.append(i)
        
        if len(available_directions) == 0:
            self.is_dead = True

        return available_directions
    
    def move(self, direction):
        """
        Move current path into a new position
        Add current position in the list of explored positions
        Add points corresponding to the move (1 point if go straight, 1000 points if turn by 90°)
        """

        #_log("Path before move (%d): %s" % (direction, self), 3)
        # Add current position to explored positions
        self.explored.append(self.position)

        # Add 1 point everytime
        self.points += 1

        if direction != 0:
            # Add 1000 points as we turn by +/-90°
            self.points += 1000
            # Update direction
            cur_dir_idx = Path.dir_array.index(self.direction)
            self.direction = Path.dir_array[(cur_dir_idx+direction)%4]
            
        # Calculate delta x and delta y based on updated direction
        (dx,dy) = s_to_xy(Path.dir_dict[self.direction])
        
        # Update position
        self.x += dx
        self.y += dy
        self.position = xy_to_s(self.x,self.y)

        #_log("Path after move: %s" % (self), 3)
            

    def is_on_end(self):
        """
        Return True if the path arrived to the end of the map
        """
        #_log("Path %s: is_on_end(). x=%d y=%d. Map=%d" % (self, self.x, self.y, len(self.map)), 3)
        try:
            return self.map[self.x][self.y] == 'E'
        except IndexError:
            return False
            


def print_interractive_map(path, all_paths):
    all_explored = []
    best_path = all_paths[0]
    for p in all_paths:
        if p.is_on_end():
            best_path = p
            break
    
    for p in all_paths:
        all_explored += p.explored
        if p.is_on_end() and p.points < best_path.points:
            best_path = p

    map = Path.map

    print("Found %d paths" % (len(all_paths)))
    for x in range(len(map)):
        for y in range(len(map[x])):
            if xy_to_s(x,y) in path.explored:
                print("\x1b[1;33;40mO\x1b[0m", end="")
            elif xy_to_s(x,y) in best_path.explored:
                print("\x1b[1;32;40mO\x1b[0m", end="")
            elif xy_to_s(x,y) in all_explored:
                print("\x1b[0;90;40mO\x1b[0m", end="")
            else:
                print(map[x][y], end="")
        print("")

    time.sleep(0.1)
    
     

def explore_path(path):
    """
    Explore a starting path and give all possible pathes to reach the end.
    From a current path (which has a current position, direction and alrady explored positions),
    identify all directions where we can go.
    Explore these directions.
    In case we reach the end, return the path as a valid one.
    """
    unfinished_paths = [path]
    finished_paths = []
    best_points = None

    while unfinished_paths:
        p = unfinished_paths.pop(0)
        #_log("Path %s: start exploring" % (p), 2)
        _log("%d path in queue. Exploring path %s" % (len(unfinished_paths), p))
        
        if args.interactive:
            os.system("clear")
            print("Lowest number of points for a finished path: %s" % (best_points))
            print_interractive_map(p, [p] + unfinished_paths + finished_paths)

        if p.is_on_end():
            _log("Found a path that goes to the end: %s" % (p))
            finished_paths.append(p)
            best_points = min([p.points for p in finished_paths])
            continue

        directions = p.get_available_directions()
        if len(directions) == 0:
            _log("Path %s: No possible new direction" % (path), 2)
            continue
        for direction in directions:
            np = Path(p.position, p.direction, p.explored, p.points)
            np.move(direction)
            # Ignore paths that already have more points than the best path.
            if best_points and np.points >= best_points:
                continue
            unfinished_paths.insert(0, np)
        del(p)
    
    return finished_paths


#def explore_pathes(path, paths = []):
#    if not path in paths:
#        paths.append(path)
#
#    if args.interactive:
#        print_interractive_map(paths)
#
#    _log("Path %s: start exploring" % (path))
#    if path.is_on_end():
#        _log("Path %s: arrived to the end!" % (path))
#        return paths
#
#    cur_pos = path.position
#    cur_direction = path.direction
#    cur_explored = path.explored
#
#    directions = path.get_available_directions()
#    if len(directions) == 0:
#        _log("Path %s: No possible new direction" % (path))
#        paths.remove(path)
#    else:
#        _log("Path %s: Found %d possible direcions" % (path, len(directions)))
#    
#    for direction in path.get_available_directions():
#        if direction == 0:
#            p = path
#        else:
#            p = Path(cur_pos, cur_direction, cur_explored)
#        p.move(direction)
#        explore_pathes(p, paths)
#
#    return paths

    
def find_shortest_path(map):
     # Find start
    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == "S":
                start_pos = xy_to_s(x,y)

    path = Path(start_pos)
    path.set_map(map)
    pathes = explore_path(path)

    best_path = pathes[0]
    for path in pathes:
        if path.points < best_path.points:
            best_path = path
    print_interractive_map(best_path, pathes)
    _log("Shortest path is %s" % (best_path))

    return best_path

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

def find_all_paths(map, graph, start, end):
    valid = []
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
                    valid.append(new_path)
                
            explored.append(node)
    

    return valid


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
                current = xy_to_s(x,y)
                graph[current] = []
                # Explore neighbors
                neighbors = []
                for (dx,dy) in [s_to_xy(dir) for dir in directions]:
                    (nx,ny) = (x+dx,y+dy)
                    if nx < 0 or nx >= len(map) or ny < 0 or ny >= len(map):
                        continue
                    if map[x+dx][y+dy] != "#":
                        neighbors.append(xy_to_s(x+dx,y+dy))
                for parent in neighbors:
                    for next in neighbors:
                        if parent == next:
                            continue
                        points = 1
                        dir = get_new_dir(parent, current)
                        if has_turn(current, dir, next):
                            points += 1000
                        graph["%s-%s" % (parent, current)].append("%s:%s" % (next, points))
    return graph

def get_new_dir(cur_dir, turn):
    dirs = ['>', 'v', '<', '^']
    new_dir_idx = (dirs.index(cur_dir) + turn) % 4
    return dirs[new_dir_idx]

def get_dir_delta(dir):
    dir_to_delta = {
        '>': '0,1',
        'v': '1,0',
        '<': '0,-1',
        '^': '-1,0',
    }
    return dir_to_delta(dir)

def has_turn(old_xy, old_dir, new_xy):
    return old_dir == get_new_dir(old_xy, new_xy)

def get_new_dir(old_pos, new_pos):
    delta_to_dir = {
        '0,1' : '>',
        '1,0' : 'v',
        '0,-1': '<',
        '-1,0': '^',
    }

    (oldx, oldy) = s_to_xy(old_pos)
    (newx, newy) = s_to_xy(new_pos)
    (dx,dy) = (newx-oldx, newy-oldy)

    return delta_to_dir[xy_to_s(dx,dy)]



def get_points(path):
    old_dir = '>'
    old_pos = path.pop(0)
    points = 0

    for new_pos in path:
        points += 1
        new_dir = get_new_dir(old_pos, new_pos)
        if new_dir != old_dir:
            points += 1000
        old_dir = new_dir
        old_pos = new_pos
    
    return points


def get_result(raw_data):
    """
    
    """
    total = 0

    map = read_data_map(raw_data)
    
    print_map(map)

    graph = build_graph(map)

    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == "S":
                start_pos = xy_to_s(x,y)
            elif map[x][y] == "E":
                end_pos =  xy_to_s(x,y)

    paths = find_all_paths(map, graph, start_pos, end_pos)
    _log("Found %d valid paths: %s" % (len(paths), paths))

    best_path = paths[0]
    best_paths_points = get_points(best_path)
    for p in paths[1:]:
        points = get_points(p)
        if points < best_paths_points:
            best_paths_points = points
            best_path = p

    _log("Best path has %d points with len %d: %s" % (best_paths_points, len(best_path), best_path))
    print_explored_map(map, best_path, paths)

    #best_path = find_shortest_path(map)
    total = best_paths_points

    return total
    
   
# Do not remove me

print_result(get_result(raw_data))