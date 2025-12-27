#!/usr/bin/env python3

import argparse
import re
import os
import sys
import time
import math
from collections import defaultdict
import matplotlib.pyplot as plt


# =============================================================================
# Generic code
# =============================================================================

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, nargs='?', default="input.txt", help="Input file")
parser.add_argument('--verbose', '-v', action='count', default=0, help="Increase verbosity level")
parser.add_argument('--interactive', '-i', action='store_true', default=False, help="Run in interactive mode")
parser.add_argument('--debug', '-d', action='store_true', default=False, help="Enable debug mode")


args = parser.parse_args()
if args.interactive:
    args.verbose = 0

def _log(msg, level = 1):
    if level <= args.verbose:
        print("[DEBUG] %s" % (msg))

def print_map(map, level = 1):
    output = ""
    if level <= args.verbose:
        for y in range(len(map)):
            for x in range(len(map[y])):
                output += map[y][x]
            output += "\n"
        print(output)

def print_result(result):
    if args.verbose > 0: 
        print(_c("\n================", "yellow"))
    print(_c("Result: %s" % (result), "yellow", bold=True))

if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


with open(args.input_file) as f:
    raw_data = f.read().strip()

def yx_to_s(y, x):
    return "%d,%d" % (y,x)

def s_to_yx(yx):
    (y, x) = yx.split(",")
    return (int(y), int(x))

def in_map(map, y, x):
    """
    Tell if a given location is inside (True) or outside (False) of a given map (2D array)
    """
    if y < 0 or y >= len(map):
        return False
    if x < 0 or x >= len(map[y]):
        return False
    return True

def copy_map(map):
    """
    Create a copy of a map
    """
    new_map = []
    for y in range(len(map)):
        new_map.append(map[y].copy())
    return new_map

def read_data_map(raw_data):
    return [[x for x in line] for line in raw_data.split("\n")]

def _c(text, fg=None, bg=None, bold=False, italic=False, dark=False, underline=False, reverse=False, strike=False):
    color_map = {
        "black": 0,
        "gray": 0,
        "grey": 0,
        "red": 1,
        "green": 2,
        "brown": 3,
        "yellow": 3,
        "blue": 4,
        "purple": 5,
        "cyan": 6,
        "white": 7,
    }

    colors=[]
    color_text = ""
    if bold:
      colors.append("1")
    if dark:
      colors.append("2")
    if italic:
      colors.append("3")
    if underline:
      colors.append("4")
    if reverse:
      colors.append("7")
    if reverse:
      colors.append("9")
    if fg:
        colors.append("3%d"%(color_map[fg]))
    if bg:
        colors.append("4%d"%(color_map[bg]))
    if len(colors) > 0:
        color_text = '\033[%sm' % (';'.join(colors))
    

    return "%s%s%s" % (color_text, text, '\033[0m')

class Map:
    def __init__(self, width: int = 0, height: int = 0, fill: str = ".", map: list = None):
        if map:
            if not self.__checkmap(map):
                raise Exception("Map provided is not valid")
            self.map = self.__copymap(map)
        else:
            self.map = []
            for y in range(height):
                tmp = [fill for x in range(width)]
                self.map.append(tmp)

        self.snapshots = {}
        self.height = len(self.map)
        self.width = len(self.map[0])

    def set_point(self, val: str, x: int, y: int) -> None:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise IndexError("point (%d,%d) is outside of the map %dx%d" % (x, y, self.width, self.height))
        
        self.map[y][x] = val
        
    def set_area(self, val: str, x1: int, y1: int, x2: int, y2: int) -> None:
        if  x1 < 0 or y1 < 0 or x1 >= self.width or y1 >= self.height or \
            x2 < 0 or y2 < 0 or x2 >= self.width or y2 >= self.height:
            raise IndexError("p1 (%d,%d) or p2 (%d,%d) is outside of the map %dx%d" % (x1, y1, x2, y2, self.width, self.height))
        
        min_c = (min(x1, x2), min(y1, y2))
        max_c = (max(x1, x2), max(y1, y2))

        for y in range(min_c[1], max_c[1] + 1):
            for x in range(min_c[0], max_c[0] + 1):
                self.map[y][x] = val

    def set_line(self, val: str, x1: int, y1: int, x2: int, y2: int) -> None:
        if not (x1 == x2 or y1 == y2):
            raise Exception("A line must have points that share same x or same y")
        
        self.set_area(val, x1, y1, x2, y2)

    def set(self, val: str, x1: int, y1: int, x2: int = None, y2: int = None) -> None:
        if x2 and y2:
            self.set_area(val, x1, y1, x2, y2)
        else:
            self.set_point(val, x1, y1)

    def get(self, x: int, y: int) -> str:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise IndexError("x or y (%d,%d) is outside of the map %dx%d" % (x, y, self.width, self.height))
        return self.map[y][x]

    def snapshot(self, snapshot_name):
        """
        Save current version of the map into a named snapshot.
        Can be restored later with `restore` function.
        
        :param snapshot_name: Name of the snapshot
        """
        self.snapshots[snapshot_name] = self.__copymap(self.map)

    def restore(self, snapshot_name):
        if not snapshot_name in self.snapshots:
            raise IndexError("Map snapshot '%s' does not exist" % (snapshot_name))
        
        self.map = self.__copymap(self.snapshots[snapshot_name])

    def get_snapshot(self, snapshot_name):
        if not snapshot_name in self.snapshots:
            raise IndexError("Map snapshot '%s' does not exist" % (snapshot_name))
    
        return self.__copymap(self.snapshots[snapshot_name])

    def __checkmap(self, map):
        """
        Ensure that a given map is valid:
        - width must be the same accross all height
        
        :param map: A map to check
        """
        # Ensure that width is the same on all height
        expected_width = len(map[0])
        for y in range(len(map)):
            if len(map[y]) != expected_width:
                return False
        return True

    def __copymap(self, map):
        """
        Create a copy of a map
        """
        new_map = []
        for y in range(len(map)):
            new_map.append(map[y].copy())
        return new_map
    
    def __repr__(self):
        output = ""
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                output += self.map[y][x]
            output += "\n"
        return output

# =============================================================================
# Puzzle code
# =============================================================================

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def set(self, axis: str, val: int):
        if axis == "x":
            self.x = val
        else:
            self.y = val
    
    def get(self, axis):
        if axis == "x":
            return self.x
        else:
            return self.y

    def __repr__(self):
        return str((self.x, self.y))
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

class Line:
    """
    A Line is defined by 2 points, each being describe by a (x,y) coordonate.
    Every point between these 2 points is part of the Line.
    A line must be vertical or horizontal. No diagonal is allowed
    """
    def __init__(self, p1: Point, p2: Point):
        if p1.x == p2.x:
            # Same x = vertical line
            self.type = "vertical"
            
        elif p1.y == p2.y:
            # Same y = horizontal line
            self.type = "horizontal"
        else:
            raise Exception("The line must be vertical or horizontal")

        self.p1 = Point(min(p1.x, p2.x), min(p1.y, p2.y))
        self.p2 = Point(max(p1.x, p2.x), max(p1.y, p2.y))

    def contains(self, p: Point):
        """
        Tell if point (x,y) is part of the line
        
        :param p: Point to check
        """
        return p.x >= self.p1.x and p.x <= self.p2.x and \
            p.y >= self.p1.y and p.y <= self.p2.y
    
    def overlays(self, l: Line, ignore_axis = None):
        """
        Tells if a Line is overlayed by the line
        
        :param l: Line to check
        :type l: Line
        :param ignore_axis: Tell to ignore a given axis
        """
        if not ignore_axis == "x":
            if self.p1.x > l.p2.x or self.p2.x < l.p1.x:
                return False
        
        if not ignore_axis == "y":
            if self.p1.y > l.p2.y or self.p2.y < l.p2.y:
                return False

        return True
    
    def is_horizontal(self):
        return self.type == "horizontal"

    def is_vertical(self):
        return self.type == "vertical"
    
    def len(self):
        if self.is_horizontal():
            return (self.p2.x - self.p1.x) + 1
        else:
            return (self.p2.y - self.p1.y) + 1
        
    def __repr__(self):
        return "Line[%s->%s]" % (self.p1,self.p2)
    
    def __hash__(self):
        return hash((self.p1, self.p2))
    
    def __eq__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return self.p1 == other.p1 and self.p2 == other.p2
    
class Rectangle:
    def __init__(self, corner1: Point, corner2: Point):
        c1 = corner1
        c2 = corner2

        self.topleft = Point(min(c1.x, c2.x), min(c1.y, c2.y))
        self.topright = Point(max(c1.x, c2.x), min(c1.y, c2.y))
        self.bottomright = Point(max(c1.x, c2.x), max(c1.y, c2.y))
        self.bottomleft = Point(min(c1.x, c2.x), max(c1.y, c2.y))

        self.top = Line(self.topleft, self.topright)
        self.right = Line(self.topright, self.bottomright)
        self.bottom = Line(self.bottomright, self.bottomleft)
        self.left = Line (self.bottomleft, self.topleft)

        self.lines = [self.top, self.right, self.bottom, self.top]
        self.points = [self.topleft, self.topright, self.bottomright, self.bottomleft]

        self.hlines = [self.top, self.bottom]
        self.vlines = [self.left, self.right]

    def area(self):
        return self.top.len() * self.left.len()
    
    def __repr__(self):
        return "Rectangle[%s->%s]" % (self.topleft, self.bottomright)
    
    def __hash__(self):
        return hash((self.topleft, self.bottomright))
    
    def __eq__(self, other):
        if not isinstance(other, Rectangle):
            return NotImplemented
        return self.topleft == other.topleft and self.bottomright == other.bottomright


# define a class to manage a polygon
class Polygon:
    def __init__(self, points: list[Point]):
        self.points = points
        
        self.lines: list[Line] = []
        self.hlines: list[Line] = []
        self.vlines: list[Line] = []


        self.maxx: int = 0
        self.maxy: int = 0

        # Now create lines, with a distinction between veritcal and horizontal ones
        for i in range(len(points)):
            p1 = points[i]
            if i < len(points) -1:
                p2 = points[i+1]
            else:
                p2 = points[0]

            line = Line(p1, p2)
            self.lines.append(line)
            if line.is_vertical():
                self.vlines.append(line)
            else:
                self.hlines.append(line)

            if p1.x > self.maxx:
                self.maxx = p1.x
            if p1.y > self.maxy:
                self.maxy = p1.y
    
    def contains_area(self, area: Rectangle) -> bool:
        """
        Return True if area is contained in the polygon
        
        :param area: area to check
        :type area: Rectangle
        :return: True or False
        :rtype: bool
        """
        
        # To know if a rectangle is contained in the polygon, we apply this logic:
        # - for top line of the rectangle:
        #   - select horizontal lines of the polygon that are above (y is <=)
        #   - Merge all these lines into 1 or multiple contigus lines (ie, 1-3 + 2-5 => 1-5). We don't
        #     care about y in that case.
        #   - Check that one of the merged line covers at 100% the size of the top line of the rectangle
        # - repeat logic for right, bottom and left

        matched_top = []
        matched_bottom = []
        for hline in self.hlines:
            if hline.p1.y <= area.top.p1.y:
                # Keep only lines that are in the x-range of the top line
                if hline.overlays(area.top, ignore_axis="y"):
                    matched_top.append(hline)
            elif hline.p1.y >= area.bottom.p1.y:
                if hline.overlays(area.bottom, ignore_axis="y"):
                    matched_bottom.append(hline)
        
        # Get contiguous segments formed by all lines from the polygon above/below the rectangle
        top_segments = self.__get_segments([l for l in matched_top], "x")
        bottom_segments = self.__get_segments([l for l in matched_bottom], "x")

        # Check if the rectangle top/bottom is covered by the segments calculated above.
        # If not, it means we are outside of the polygon
        if not self.__fullfill(area.top, top_segments, "x"):
            return False
        if not self.__fullfill(area.bottom, bottom_segments, "x"):
            return False


        # Apply same logic with left/right
        matched_left = []
        matched_right = []
        for vline in self.vlines:
            if vline.p1.x <= area.left.p1.x:
                matched_left.append(vline)
            elif vline.p1.x >= area.right.p1.x:
                matched_right.append(vline)

        left_segments = self.__get_segments([l for l in matched_left], "y")
        right_segments =  self.__get_segments([l for l in matched_right], "y")

        if not self.__fullfill(area.left, left_segments, "y"):
            return False
        if not self.__fullfill(area.right, right_segments, "y"):
            return False

        # If we are here, it means the rectangle is inside the polygon
        return True
        
    def __get_segments(self, lines: list[Line], axis: str) -> list[Line]:
        """
        From a list of lines, reduce all of them to a minimum number of continuous lines
        on a given axis.
        For example, if we work on x axis, lines can be merged together on "x", even if they
        are not on the same y.
        
        :param lines: lines to assemble
        :param axis: On which axis (x or y) to work. The other axis is ignored.
        """

        if len(lines) == 0:
            return []

        # First, sort lines by the given axis, from lowest to greatest
        ordered_lines = sorted(lines, key=lambda l: l.p1.get(axis))

        # segments must contain a copy of lines, because lines contains actual lines from the polygon
        # Any "set" operation is destructive
        segments: list[Line] = [Line(ordered_lines[0].p1, ordered_lines[0].p2)]
        for l in ordered_lines:
            s = segments.pop()
            if l.p1.get(axis) <= s.p2.get(axis):
                # Line start before segment, so we could extend segment
                if l.p2.get(axis) > s.p2.get(axis):
                    # Line ends after segment, so we extend it.
                    s.p2.set(axis, l.p2.get(axis))
                else:
                    # line ends before segment. Do nothing
                    pass
                segments.append(s)
            else:
                # line start after existing segment. Create a new segment
                segments.append(s)
                segments.append(Line(l.p1, l.p2))            
        
        return segments

    def __fullfill(self, line, segments, axis):
        """
        Check that at least one segment from segments covers at 100% the line, on a given axis
        
        :param line: line that must be covered
        :param segments: List of segments to check if they cover the line
        :param axis: axis on which to check. The other axis is ignored
        """

        for s in segments:
            if s.p1.get(axis) <= line.p1.get(axis) and s.p2.get(axis) >= line.p2.get(axis):
                return True
        return False

    def get_map(self) -> Map:
        map = Map(self.maxx + 3, self.maxy + 2)

        # set walls of polygon
        for line in self.lines:
            map.set("X", line.p1.x, line.p1.y, line.p2.x, line.p2.y)
            map.set("#", line.p1.x, line.p1.y)
            map.set("#", line.p2.x, line.p2.y)

        return map
    
    def __repr__(self) -> None:
        return str(self.get_map())
                    
                


def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    points = []
    for line in raw_data.split("\n"):
        (x,y) = line.split(",")
        points.append(Point(int(x), int(y)))

    polygon = Polygon(points)

    if args.input_file == "sample.txt" and args.verbose >= 2:
        print(polygon)
        map = polygon.get_map()
        map.snapshot("init")

    max_area = 0
    cur_p = 0
    for p1 in points:
        for p2 in points[cur_p+1:]:
            rec = Rectangle(p1, p2)
            area = rec.area()
            _log("Checking area formed by %s<->%s [area=%d|max=%d]" % (p1, p2, area, max_area), 2)
            if area <= max_area:
                # Do not check rectangles we already know are smaller than largest area
                continue
            if args.verbose >= 2 and args.input_file == "sample.txt":
                map.restore("init")
                map.set_area("0", p1.x, p1.y, p2.x, p2.y)
                map.set_point(_c("0", "yellow"), p1.x, p1.y)
                map.set_point(_c("0", "yellow"), p2.x, p2.y)
                print(map)
            if polygon.contains_area(rec):
                _log(_c("Rectangle formed by %s<->%s is inside the polygon" % (p1, p2), "green"), 2)
                if area > max_area:
                    _log(_c("New max area of %d with points %s and %s" % (area, p1, p2,), "yellow"))
                    max_area = area
            else:
                _log(_c("Rectangle formed by %s<->%s is not inside the polygon" % (p1, p2), "red"), 2)

            if args.debug and rec == Rectangle(Point(5953,67629), Point(94872,50262)):
                fig, ax = plt.subplots()
    
                for l in polygon.lines:
                    ax.plot([l.p1.x,l.p2.x], [l.p1.y,l.p2.y])
                
                rect = plt.Rectangle((rec.topleft.x, rec.topleft.y), rec.topright.x - rec.topleft.x, rec.bottomleft.y - rec.topleft.y, linewidth=3, edgecolor="red")
                ax.add_patch(rect)
                ax.set_aspect("equal")
                plt.show()
        cur_p += 1

    total = max_area
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))