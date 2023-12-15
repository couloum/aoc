#!/usr/bin/env python3

import argparse
import re
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, nargs='?', default="input.txt", help="Input file")
parser.add_argument('--verbose', '-v', action='count', default=0, help="Increase verbosity level")


args = parser.parse_args()

def _log(msg, level = 1):
    if level <= args.verbose:
        print("[DEBUG] %s" % (msg))

def print_map(map):
    for x in range(len(map)):
        for y in range(len(map[x])):
            print(map[x][y], end="")
        print("")


score_map = {
    'A': 14,
    'K': 13,
    'Q': 12,
    'J': 11,
    'T': 10,
}

def read_data(raw_data):
    hands = []
    for line in raw_data.split("\n"):
        tmp = line.split(" ")
        hands.append((tmp[0], int(tmp[1])))

    return hands

def card_to_score(card):
    if card.isdigit():
        return int(card)
    return score_map[card]

def hands_to_score(hands):
    """
    Transform hands into score base on specific algorithm:
    A=14
    K=13
    Q=12
    J=11
    T=10
    9-2=9-2

    Addition all cards together based on their order.
    1st card = value * 10^4
    2nd card = value * 10^3
    ...
    5th card = value * 10^0

    Then add a score based on combination:
    - Five of a kind:   6 * 10^11
    - Four of a kind:   5 * 10^11
    - Full house:       4 * 10^11
    - Three of a kind:  3 * 10^11
    - Two pair:         2 * 10^11
    - Pair:             1 * 10^11
    - High card:        0
    """
    hands_score = []
    for hand in hands:
        hand_cards = hand[0]
        hand_bid = hand[1]
        score = 0
        idx = 0
        card_count = {}
        for card in hand_cards:
            score += card_to_score(card) * pow(10, 2*(4-idx))
            if not card in card_count:
                card_count[card] = 0
            card_count[card] += 1

            idx += 1

        # Now count score for types:
        for type in card_count.values():
            if type == 5:
                score += 6 * pow(10, 11)
            elif type == 4:
                score += 5 * pow(10, 11)
            elif type == 3:
                score += 3 * pow(10, 11)
            elif type == 2:
                score += pow(10, 11)
        
        hands_score.append((hand_cards, score, hand_bid))

    hands_score.sort(key=lambda x: x[1])
    return hands_score

def part1(raw_data):
    total = 0
    hands = read_data(raw_data)
    _log("hands: %s" % (hands))
    
    hands_score = hands_to_score(hands)
    _log("Hand scores: %s" % (hands_score))

    for idx in range(len(hands_score)):
        score = (idx+1) * hands_score[idx][2]
        total += score
        _log("[%03d] hand [%s] with value of %s. Bid=%d Score=%d. Total=%d" % (idx, hands_score[idx][0], hands_score[idx][1], hands_score[idx][2], score, total))
        

    return total
    



if not os.path.isfile(args.input_file):
    print("Error: file %s does not exist." % (args.input_file), file=sys.stderr)
    sys.exit(1)


with open(args.input_file) as f:
    raw_data = f.read().strip()


result = part1(raw_data)
if args.verbose > 0: 
    print("\n================")
print("Result: %s" % (result))

        
        
