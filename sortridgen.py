#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sorting Riddle Generator
"""


import argparse
import collections
import csv
import os


DEF_DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")
DEF_DICTFILE_PATH = os.path.join(DEF_DICT_DIR, "english/ejdict_level0_words.csv")
DEF_SUBDICT_PATHS = (
    os.path.join(DEF_DICT_DIR, "english/ejdict_level1_words.csv"),
    os.path.join(DEF_DICT_DIR, "english/ejdict_level2_words.csv")
)
DEF_WORDLEN_MIN = 5


def extract_words(
    maindic=DEF_DICTFILE_PATH,
    subdics=DEF_SUBDICT_PATHS,
    wordlen_min=DEF_WORDLEN_MIN):
    # read the main dictionary
    main_orig2sorted = dict()
    sorted2origs = collections.defaultdict(set)
    with open(maindic, encoding="utf-8") as mdf:
        reader = csv.DictReader(df)
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
        "--maindic",
        help="the path to the main dictionary file (*.csv).",
        default=DEF_DICTFILE_PATH
    )
    parser.add_argument(
        "--subdic",
        help="the path to the sub dictionary files (*.csv).",
        default=DEF_SUBDICT_PATHS,
        action="append"
    )
    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()