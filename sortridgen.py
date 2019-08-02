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
import itertools
import json
import os
import random
import sys


DEF_DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")
DEF_PRESET_DIR = os.path.join(os.path.dirname(__file__), "presets")
DEF_PRESET_NAME = "default.json"
DEF_WORDLEN_MIN = 5


class RiddleGeneratorError(Exception):
    pass


def find_file(path, def_dir):
    if os.path.exists(path):
        return os.path.abspath(path)
    else:
        path_cand = os.path.join(def_dir, path)
        if os.path.exists(path_cand):
            return os.path.abspath(path_cand)
        else:
            raise RiddleGeneratorError("Could not find {}".format(path))


class RiddleDictionary(object):

    def __init__(self, dict_path):
        self.dict_name = os.path.basename(dict_path)
        self.dict_file = find_file(dict_path, DEF_DICT_DIR)
        self.origwords = []
        self.sorted2origs = collections.defaultdict(set)
        with open(self.dict_file, encoding="utf-8") as df:
            reader = csv.DictReader(df)
            for row in reader:
                orig_word = row["orig_word"]
                sorted_word = row["sorted_word"]
                self.origwords.append(orig_word)
                self.sorted2origs[sorted_word].add(orig_word)


class RiddlePreset(object):

    def __init__(self, preset_path):
        self.preset_name = os.path.basename(preset_path)
        self.preset_file = find_file(preset_path, DEF_PRESET_DIR)
        self.preset_args = None
        with open(find_file(preset_path, DEF_PRESET_NAME), encoding="utf-8") as def_pre:
            self.preset_args = json.load(def_pre)
        with open(self.preset_file, encoding="utf-8") as pre:
            new_args = json.load(pre)
            for key, val in new_args.items():
                self.preset_args[key] = val.replace(":default:", self.preset_args[key])
        self.preset_args["maindics"] = [dic.replace(":dictionaries:", DEF_DICT_DIR) for dic in self.preset_args["maindics"]]
        self.preset_args["subdics"] = [dic.replace(":dictionaries:", DEF_DICT_DIR) for dic in self.preset_args["subdics"]]
        self.maindics = [RiddleDictionary(dic) for dic in self.preset_args["maindics"]]
        self.subdics = [RiddleDictionary(dic) for dic in self.preset_args["subdics"]]
        self.prob_sorted_words = set()
        for maindic in self.maindics:
            self.prob_sorted_words.update(maindic.sorted2origs.keys())
        self.all_sorted2origs = collections.defaultdict(set)
        for dic in itertools.chain(self.maindics, self.subdics):
            for k, vals in dic.sorted2origs.items():
                self.all_sorted2origs[k].update(vals)



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