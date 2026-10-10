import sys
import random  # Select each line with 1% probability

if len(sys.argv) != 2:
    sys.exit("Usage: python3 samplit-baijunzhang.py filename")

with open(sys.argv[1], "r", encoding="utf-8") as file:
    for line in file:
        if random.random() < 0.01:
            print(line, end="")
