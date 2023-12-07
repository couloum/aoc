#!/usr/bin/env python3

import re

numbers = {
#        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9
        }

def rreplace(s, old, new, occurence):
    li = s.rsplit(old, occurence)
    return new.join(li)

def letters_to_num(line):
    """
    Replace first occurence of a number written in letters with equivalent number.
    AND
    Replace last occurence of a number written in letters with equivalent number.
    """


    # Find 1st and last occurence of a number
    x = re.search("\d", line)

    # Find first and last occurences of a number written in letters
    first_idx = 99
    for n in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        try:
            first_idx = min(line.index(str(n)), first_idx)
        except:
            pass
    first_num = ""
    last_idx = -1
    for n in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        try:
            last_idx = min(line.rindex(str(n)), last_idx)
        except:
            pass
    last_num = ""
    print("Initial position: min=%s max=%s" % (first_idx, last_idx))
    for num in numbers.keys():
        print("Trying to find letter %s in %s" % (num, line))
        try:
            idx = line.index(num)
            print("[MIN] Found 1 occurence at position %s" % (idx))
            if idx < first_idx:
                print("[MIN] New min position: %s (previous: %s)" % (idx, first_idx))
                first_idx = idx
                first_num = num
        except:
            pass

        try:
            idx = line.rindex(num)
            print("[MAX] Found 1 occurence at position %s" % (idx))
            if idx > last_idx:
                print("[MAX] New max position: %s (previous: %s)" % (idx, last_idx))
                last_idx = idx
                last_num = num
        except:
            pass

    if first_num != "" and first_idx < 999:
        line = line.replace(first_num, str(numbers[first_num]), 1)
    if last_num != "" and last_idx > -1 and last_idx != first_idx:
        line = rreplace(line, last_num, str(numbers[last_num]), 1)
    return line

result = 0
with open('input.txt') as f:
    for line in f:
        if not line:
            break
        line = line.strip()
        print("Initial line: %s" % (line))
        line = letters_to_num(line)
        print("Line after letters_to_num(): %s" % (line))
        results = re.findall("([0-9])", line)
        print(results)
        coordonates = results[0] + "" + results[-1]
        result += int(coordonates)
        print("Numbers: %s - Coordonates: %s - Total: %s" % (results, coordonates, result))
        print("")

print("===========")
print("Result: %s" % (result))

        
        
