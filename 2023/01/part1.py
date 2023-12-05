#!/usr/bin/env python3

import re

result = 0
with open('input.txt') as f:
    for line in f:
        if not line:
            break
        #print(line.strip())
        results = re.findall("[0-9]", line)
        #print(results)
        coordonates = results[0] + "" + results[-1]
        result += int(coordonates)
        print("Numbers: %s - Coordonates: %s - Total: %s" % (results, coordonates, result))

print("===========")
print("Result: %s" % (result))

        
        
