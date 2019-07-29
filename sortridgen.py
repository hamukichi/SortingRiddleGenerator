#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sorting Riddle Generator
"""

__author__ = "Hamukichi (Nombiri)"
__version__ = "0.0.1"
__date__ = "2019-07-29"
__license__ = "MIT License"


import argparse
import collections
import csv
import json
import os
import random
import sys


DEF_DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")
DEF_PRESET_DIR = os.path.join(os.path.dirname(__file__), "presets")
DEF_PRESET_NAME = "ejdic-hand-level2"
DEF_WORDLEN_MIN = 5


def parse_preset(preset_name, preset_dir=DEF_PRESET_DIR, dict_dir=DEF_DICT_DIR):
    preset_name = preset_name.replace(".json", "")
    preset_file = os.path.join(preset_dir, preset_name + ".json")
    maindicts = []
    subdicts = []
    with open(preset_file, encoding="utf-8") as pre:
        pre_data = json.load(pre)
        maindicts.extend(d.replace(":dictionaries:", dict_dir) for d in pre_data["maindicts"])
        subdicts.extend(d.replace(":dictionaries:", dict_dir) for d in pre_data["subdicts"])
    return maindicts, subdicts


def extract_words(
    maindics, subdics,
    wordlen_min=DEF_WORDLEN_MIN):
    # read the main dictionary
    main_orig2sorted = dict()
    sorted2origs = collections.defaultdict(set)
    for maindic in maindics:
        with open(maindic, encoding="utf-8") as mdf:
            reader = csv.DictReader(mdf)
            for row in reader:
                orig_word = row["orig_word"]
                sorted_word = row["sorted_word"]
                if len(orig_word) >= wordlen_min:
                    main_orig2sorted[orig_word] = sorted_word
                    sorted2origs[sorted_word].add(orig_word)
    # read the sub dictionary. boiler plate...
    for subdic in subdics:
        with open(subdic, encoding="utf-8") as sdf:
            reader = csv.DictReader(sdf)
            for row in reader:
                orig_word = row["orig_word"]
                sorted_word = row["sorted_word"]
                if len(orig_word) >= wordlen_min:
                    sorted2origs[sorted_word].add(orig_word)
    return main_orig2sorted, sorted2origs


def problem_setter(main_orig2sorted, sorted2origs):
    main_orig_words = list(main_orig2sorted.keys())
    random.shuffle(main_orig_words)
    res = {"ok": 0, "optimal": 0, "other": 0, "giveup": 0}
    print("Input your answer for each problem.")
    print("Input 'HINT [number of characters (> 0)]' to obtain a hint.")
    print("Input 'GIVEUP' to give up the current problem.")
    print("Input 'EXIT' to quit.")
    for idx, orig_word in enumerate(main_orig_words, start=1):
        print()
        sorted_word = main_orig2sorted[orig_word]
        print("Question {}. {}".format(idx, sorted_word))
        while True:
            ans = input(">>> ")
            if ans == orig_word:
                print("Correct! :) The answer is {}".format(orig_word))
                res["ok"] += 1
                res["optimal"] += 1
                break
            elif ans in sorted2origs[sorted_word]:
                print("Good, {} is also one of the answers. ;)".format(ans))
                res["ok"] += 1
                res["other"] += 1
                break
            elif ans == "GIVEUP":
                print("Oops! :( The answer is {}".format(orig_word))
                res["giveup"] += 1
                break
            elif ans.startswith("HINT"):
                try:
                    _, n0 = ans.split()
                    n = int(n0)
                    assert n > 0
                except Exception:
                    print("Syntax Error. Use 'HINT [number of characters (> 0)]'")
                else:
                    hint_len = min(n, len(orig_word))
                    hint_str = orig_word[:hint_len]
                    print("Hint. The answer starts with {}".format(hint_str))
            elif ans == "EXIT":
                print("Summary (total: {} problems)".format(idx - 1))
                print("Correct: {} (optimal: {}, other: {})".format(res["ok"], res["optimal"], res["other"]))
                print("Give up: {}".format(res["giveup"]))
                print("See you again!")
                sys.exit(0)
            else:
                print("Wrong answer. Try again.")
        print("All possible answers: ", end="")
        print(*sorted2origs[sorted_word])


def main():
    """Used when this module is run as a script.
    """
    # parser
    parser = argparse.ArgumentParser(
        description="Make sorting riddles (ソートなぞなぞ in Japanese).",
        epilog="See '%(prog)s --help' for detailed information."
    )
    # add arguments
    parser.add_argument(
        "--preset",
        help="the name of preset file (*.json files in /presets/)",
        default=DEF_PRESET_NAME
    )
    args = parser.parse_args()
    maindics, subdics = parse_preset(args.preset)
    main_orig2sorted, sorted2origs = extract_words(maindics, subdics)
    problem_setter(main_orig2sorted, sorted2origs)


if __name__ == "__main__":
    main()