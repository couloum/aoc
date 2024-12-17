#!/usr/bin/env python3

import argparse
import re
import os
import sys
#import numpy as np
#import math

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

class Computer:


    def __init__(self, registers, instructions):
        self.registers = registers.copy()
        self.instructions = self.decode_instructions(instructions)
        self.cursor = 0
        self.output = []
        self.digits = len(self.instructions)

    def set_registerA(self, value):
        self.registers['A'] = value
    
    def reset(self, registers):
        self.registers = registers
        self.cursor = 0
        self.output = []

    def decode_instructions(self, instructions):
        tmp = []
        if type(instructions) == str:
            for i in instructions.split(','):
                tmp.append(int(i))
        return tmp
    
    def get_output(self):
        return str.join(",", [str(x) for x in self.output])
    
    def get_output_array(self):
        return self.output
    
    def check_digit(self, digit):

        # First ensure that we have same number of digits between output and instruction
        if len(self.output) != len(self.instructions):
            return False
        
        _log("check_digit(%d). Comparing %d with %d" % (digit, self.output[digit], self.instructions[digit]), 3)
        if self.output[digit] == self.instructions[digit]:
            return True
        return False
    
    def get_combo_operande(self, instruction):
        # Combo operands 0 through 3 represent literal values 0 through 3.
        # Combo operand 4 represents the value of register A.
        # Combo operand 5 represents the value of register B.
        # Combo operand 6 represents the value of register C.
        # Combo operand 7 is reserved and will not appear in valid programs.

        if instruction <= 3:
            return instruction
        elif instruction == 7:
            return False
        mapping = {4:'A', 5:'B', 6:'C'}
        return self.registers[mapping[instruction]]


    def process_next(self):
        """
        Process the instruction under current position of the cursor and move the cursor.
        If cursor is out of range after this operation, return False.
        Otherwise, return True
        """
        opcode = self.instructions[self.cursor]
        operande = self.instructions[self.cursor+1]
        combo_operande = self.get_combo_operande(operande)

        _log("Processing cursor=%d instruction=%d operande=%d combo_operande=%d" % (self.cursor, opcode, operande, combo_operande), 2)
        match opcode:
            case 0: #adv
                # The adv instruction (opcode 0) performs division. The numerator is the value in the A register.
                # The denominator is found by raising 2 to the power of the instruction's combo operand.
                # (So, an operand of 2 would divide A by 4 (2^2); an operand of 5 would divide A by 2^B.)
                # The result of the division operation is truncated to an integer and then written to the A register.
                val = int(self.registers['A'] / 2 ** combo_operande)
                _log("Instruction adv: store (%d / 2 ** %d) = %d in register A" % (self.registers['A'], combo_operande, val), 3)
                self.registers['A'] = val
            case 1: #bxl
                # The bxl instruction (opcode 1) calculates the bitwise XOR of register B and the instruction's literal operand,
                # then stores the result in register B.
                val = self.registers['B'] ^ operande
                _log("Instruction bxl: store (%d ^ %d) = %d in register B" % (self.registers['B'], operande, val), 3)
                self.registers['B'] = val
            case 2: #bst
                # The bst instruction (opcode 2) calculates the value of its combo operand modulo 8
                # (thereby keeping only its lowest 3 bits), then writes that value to the B register.
                val = combo_operande % 8
                _log("Instruction bst: store (%d %% 8) = %d in register B" % (combo_operande, val), 3)
                self.registers['B'] = val
            case 3: #jnz
                # The jnz instruction (opcode 3) does nothing if the A register is 0.
                # However, if the A register is not zero, it jumps by setting the instruction pointer to the value
                # of its literal operand; if this instruction jumps, the instruction pointer is not increased by 2
                # after this instruction.
                if self.registers['A'] > 0:
                    _log("Instruction jnz with register A > 0: move cursor to %d" % (operande), 3)
                    self.cursor = operande - 2
                else:
                    _log("Instruction jnz with register A = 0: do nothing", 3)
            case 4: #bxc
                # The bxc instruction (opcode 4) calculates the bitwise XOR of register B and register C,
                # then stores the result in register B. (For legacy reasons, this instruction reads an operand but ignores it.)
                val = self.registers['B'] ^ self.registers['C']
                _log("Instruction bxc: store (%d ^ %d)= %d in register B" % (self.registers['B'], self.registers['C'], val), 3)
                self.registers['B'] = val
            case 5: #out
                # The out instruction (opcode 5) calculates the value of its combo operand modulo 8, then outputs that value.
                # (If a program outputs multiple values, they are separated by commas.)
                _log("Instruction out: append (%d %% 8) = %d to the output" % (combo_operande, combo_operande%8), 3)
                self.output.append(combo_operande % 8)
            case 6: #bdv
                # The bdv instruction (opcode 6) works exactly like the adv instruction except that the result is stored
                # in the B register. (The numerator is still read from the A register.)
                val = int(self.registers['A'] / 2 ** combo_operande )
                _log("Instruction bdv: store (%d / 2 ** %d) = %d in register B" % (self.registers['A'], combo_operande, val), 3)
                self.registers['B'] = val
            case 7: #cdv
                # The cdv instruction (opcode 7) works exactly like the adv instruction except that the result is stored
                # in the C register. (The numerator is still read from the A register.)
                val = int(self.registers['A'] / 2 ** combo_operande)
                _log("Instruction bdv: store (%d / 2 ** %d) = %d in register C" % (self.registers['A'], combo_operande, val), 3)
                self.registers['C'] = val
        
        _log("Registers: %s" % (self.registers), 3)
        _log("Output: %s" % (self.output), 3)

        self.cursor += 2
        return self.cursor < len(self.instructions)


    def process_instructions(self):
        _log("Start processing all instructions", 2)
        i = 0
        while self.process_next():
            i += 1
            continue
        _log("End processing all instructions after %d rounds" % (i), 2)
        _log("Registers: %s" % (self.registers), 2)
        _log("Output: %s" % (self.output), 2)
        return self.output
    
    def get_possibilities(self, factors = []):
        """
        Identify all possible values of register A that lead to the output being similar
        as the instructions.
        For that, identify all values of register A that generate an output where last digit is same as the instruction.
        For each of these values, do the same with the digit just before
        And so on.
        The value is a factor that we multiply to 8 ** (index of digit to search)
        We use a recursive function here.
        """

        # See which digit we should search for
        # This depends on the number of factors we already identified.
        digit = len(factors) + 1
        digit_idx = self.digits - digit

        # Compute base value of register A, from the different factors we already calculated
        a = 0
        for i in range(len(factors)):
            f = factors[i]
            a += f * 8 ** (self.digits - (i+1))

        # If we are trying to find a digit that is above the number of digits from instruction, just exit.
        # This is the end of the recursion and the appropriate value (terminal recursion)
        if digit > self.digits:
            return [a]

        _log("Testing possibilities for digit %d and factors=%s" % (digit_idx, factors))

        # For each factor of the 8 ** x, test if the output match the instruction for the digit we're focusing on
        # If so, continue exploring this branch through a recursion
        possibilities = []
        for i in range(8):
            self.reset({'A': a, 'B':0, 'C': 0})
            self.process_instructions()
            _log("digit=%d a=%15d i=%d: %s <=> %s" % (digit_idx, a, i, self.output, self.instructions))
            if self.check_digit(digit_idx):
                _log("digit=%d a=%15d i=%d factors=%s : Found match %d == %d" % (digit_idx, a, i, factors, self.output[digit_idx], self.instructions[digit_idx]))
                tmp = self.get_possibilities(factors + [i])
                #tmp = []
                if len(tmp) > 0:
                    possibilities += tmp
            a += 8 ** digit_idx
        
        # If we no factor allows to match the digit, then it's a dead end
        if len(possibilities) == 0:
            _log("digit=%d a=%15d i=%d factors=%s: No match found" % (digit_idx, a, 9, factors))
            return []
        
        # If we're here, then we have some solutions
        return possibilities



global computer

def read_data_custom(raw_data):
    regexp1 = re.compile(r'Register ([ABC]): ([0-9]+)')
    regexp2 = re.compile(r'Program: (.*)')

    registers = dict()
    instructions = ""
    for line in raw_data.split("\n"):
        m = regexp1.fullmatch(line)
        if m:
            registers[m.group(1)] = int(m.group(2))
            continue
        m = regexp2.fullmatch(line)
        if m:
            instructions = m.group(1)
            continue

    return (registers, instructions)


def get_result(raw_data):
    """
    Get list of all possible values of register A that generate an outpout from the computer that
    is similar to the instructions
    """
    total = 0

    (registers, instructions) = read_data_custom(raw_data)
    _log("Registers: %s" % (registers))
    _log("Instructions: %s" % (instructions))
    
    # After some reverse engineering, we figure out that the whole computer is a counter which update
    # every increase of 8 for register A.
    # The numbers are unpredictable, but we know that a digit is added every power of 8
    # So, to get number of digits expect, count number of instructions and calculte 8 ** this number
    # Considering we have 16 digits in the input, the right value for A would be between 8^16 and 8^17, which still leaves ~2x10^15 possibilities...

    # But we can do some dicotomy as the last digit change every 8 ** (number of digit - 1)
    # And the digit at its left change every 8 ** (number of digit - 2)
    # ...
    # But, another fun things: there are multiple 8**x that can lead to same result, so we have to explore all possibilities

    computer = Computer(registers, instructions)
    instructions = [int(x) for x in instructions.split(",")]

        
    possibilities = computer.get_possibilities()
        
       
    _log("Possibilities: %s" % (possibilities))

    total = min(possibilities)
    return total
    
   
# Do not remove me

print_result(get_result(raw_data))