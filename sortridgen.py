#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sorting Riddle Generator
"""


import argparse
import os


DEF_DICT_DIR = os.path.join(__file__, "dictionaries")
DEF_DICTFILE_PATH = os.path.join(DEF_DICT_DIR, "english/ejdict_level0_words.csv")
DEF_SUBDICT_PATHS = (
    os.path.join(DEF_DICT_DIR, "english/ejdict_level1_words.csv"),
    os.path.join(DEF_DICT_DIR, "english/ejdict_level2_words.csv")
)


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
        "maindic",
        help="the path to the main dictionary file (*.csv).",
        default=DEF_DICTFILE_PATH
    )
    parser.add_argument(
        "subdic",
        help="the path to the sub dictionary files (*.csv).",
        default=DEF_SUBDICT_PATHS,
        action="append"
    )
    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()