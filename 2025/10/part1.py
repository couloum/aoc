#!/usr/bin/env python3

import argparse
import re
import os
import sys
sys.path.append("..")
#import time
#import math
from collections import defaultdict
#import matplotlib.pyplot as plt
from common.common import _c, Map


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

def print_result(result):
    if args.verbose > 0: 
        print(_c("\n================", "yellow"))
    print(_c("Result: %s" % (result), "yellow", bold=True))

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

class Node:
    def __init__(self, obj, parent = None, childs = []):
        self.obj = obj
        self.parent = parent
        self.childs = childs

    def add_child(self, obj):
        obj.parent = self
        self.childs.append(obj)

    def __repr__(self):
        return str(self.obj)

class Light:
    def __init__(self, size: int = 0, state: str = None):
        if size == 0 and not state:
            raise ValueError("You must define either a size or a state")
        
        if size > 0:
            self.size = size
            self.state = ["." for i in range(size)]
        else:
            self.size = len(state)
            self.state = [x for x in state.strip("[]")]

    def reset(self) -> None:
        """
        Reset the lights (set all lights to off)
        """
        self.state = ["." for i in range(self.size)]

    def set(self, state: str) -> None:
        """
        Set the lights to a given position
        
        :param state: State to set
        :type state: str
        """

        self.state = [ x for x in state]

    def press(self, button: list) -> None:
        """
        Change lights after having pressed a button
        
        :param button: button to press, which contains position of lights to toogle
        :type button: list
        """

        for b in button:
            # switch light on position described by the button
            self.state[b] = "#" if self.state[b] == "." else "."

    def __repr__(self):
        return "[%s]" % ("".join(self.state))
    
    def __hash__(self):
        return hash(self.state)
    
    def __eq__(self, other: Light):
        return self.state == other.state
    
class Machine:
    def __init__(self, definition: str):
        rex = re.compile(r"^\[([\.#]+)\] ([^\{]+) \{([\d,]+)\}")

        result = rex.match(definition)
        if not result:
            raise ValueError("The definition of the machine is not valid")
        
        self.definition = definition
        # desired_lights is the desired state of ligts
        self.desired_lights = Light(state=result.group(1))

        self.buttons = []
        for b in result.group(2).split(" "):
            b = b.strip("()")
            self.buttons.append(list(map(int, b.split(","))))
        
        self.joltage = result.group(3)

    
    def solve(self) -> int:
        """
        From initial lights state (all off), find which button to press to get to the desired lights state.

        To solve this, we'll explore different branches and close some. As soon as we get the desired state,
        we exit.
        We start from initial position (all lights off), and we create one branch per button press.
        We check if one state is the desired state. If yes, we exit immediately.
        We check if one state is not identical to a previous state
        
        :return: Number of buttons to press to get to the desired lights state
        :rtype: int
        """

        solved_flag = False
        level = 0
        tree = [
            [ Node(Light(self.desired_lights.size)) ]
            ]
        while not solved_flag:
            # Add the next level in tree
            tree.append([])

            # Process all states from current level
            for node in tree[level]:
                # Test all buttons
                for b in self.buttons:
                    l = Light(state=str(node))
                    old_l = Light(state=str(l))
                    # Press the button
                    l.press(b)

                    _log("Level %d | %s: Pressing button %s -> %s" % (level+1, old_l, b, l), 3)
                    # Check if the state matches the desired state
                    if l == self.desired_lights:
                        _log("This is the desired state, after %d press!" % (level + 1), 2)
                        return level + 1
                    
                    # Check if new state already exists in previous known states
                    exists_flag = False
                    for i in range(len(tree)):
                        for j in range(len(tree[i])):
                            if tree[i][j].obj == l:
                                _log("This state already exist at level %d, position %d. Ignore" % (i, j), 3)
                                exists_flag = True
                                break
                        if exists_flag:
                            break
                    if not exists_flag:
                        _log("This is a new state. Save it", 3)
                        # This state doesn't exist yet, add it to the tree
                        child_node = Node(l)
                        node.add_child(child_node)
                        tree[level+1].append(child_node)

            level += 1
            _log("List of states in level %d: %d" % (level, len(tree[level])))




    def __repr__(self):
        return "%s %s {%s}" % (
            self.desired_lights,
            " ".join(["(%s)" % (",".join(map(str,b))) for b in self.buttons]),
            self.joltage,
        )


def get_result(raw_data):
    """
    Main function to provide the result from the puzzle, with raw_data as input
    """
    # Total will be the result from the puzzle in most cases
    total = 0

    # Read inputs to get machines
    machines = []
    for line in raw_data.split("\n"):
        m = Machine(line)
        _log("Solving machine: %s" % (m))
        n = m.solve()
        _log("Machine solved after %d button press" % (n))
        total += n

    
    
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))