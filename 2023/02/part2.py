#!/usr/bin/env python3

import re

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

        min_cubes = {
            "red": 0,
            "green": 0,
            "blue": 0
        }
        for s in sets:
            cubes = s.split(', ')
            for c in cubes:
                (num, color) = c.split(' ')
                min_cubes[color] = max(int(num), min_cubes[color])

        power = min_cubes['red'] * min_cubes['green'] * min_cubes['blue']
        result += power

        print("Game %d: min_cubes=%s power=%d result=%d" % (game_id, min_cubes, power, result))
        

print("===========")
print("Result: %s" % (result))

        
        
