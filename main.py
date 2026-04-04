import argparse
import sys, os, io
from pathlib import Path
from txt_input import from_lines
import ascii_repr as ar

from z3 import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Text file describing problem to be solved.", type=Path)
    args = parser.parse_args()

    if not args.input_file.is_file():
        print(f"Error: {args.input_file} is not a file.")
        sys.exit(1)
    with open(args.input_file, "r") as f:
        lines = f.readlines()
    puzzle = from_lines(lines)
    print(ar.repr_puzzle(puzzle))