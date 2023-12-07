#!/usr/bin/env python3

import re

max_cubes = {
    "red": 12,
    "green": 13,
    "blue": 14,
}

result = 0
with open('input.txt') as f:
    for line in f:
        if not line:
            break
        line = line.strip()

        matches = re.findall("Game (\d+): (.*)", line)
        print(matches)
        game_id = int(matches[0][0])
        sets = matches[0][1].split('; ')

        impossible_flag = 0
        for s in sets:
            cubes = s.split(', ')
            for c in cubes:
                (num, color) = c.split(' ')
                if int(num) > max_cubes[color]:
                    print("Warning %s (>%s) %s cubes in game ID %d" % (num, max_cubes[color], color, game_id))
                    impossible_flag = 1

        result += game_id if impossible_flag == 0 else 0
        

print("===========")
print("Result: %s" % (result))

        
        
