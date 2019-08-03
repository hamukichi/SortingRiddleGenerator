#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sorting Riddle Generator
"""

__author__ = "Hamukichi (Nombiri)"
__version__ = "0.1.0"
__date__ = "2019-08-03"
__license__ = "MIT License"


import argparse
import collections
import csv
import itertools
import json
import logging
import os
import pathlib
import random


PROG_ROOT_DIR = pathlib.Path(__file__).parent.resolve()
DEF_DICT_DIR = os.path.join(PROG_ROOT_DIR, "dictionaries")
DEF_PRESET_DIR = os.path.join(PROG_ROOT_DIR, "presets")
DEF_PRESET_NAME = "default.json"
DEF_SRG_LOGGER = logging.getLogger(__name__)
DEF_SRG_LOGGER.addHandler(logging.NullHandler())


class RiddleGeneratorError(Exception):
    pass


def locate_file(path, default_directory, logger=DEF_SRG_LOGGER):
    path = path.replace("/", os.sep)
    if os.path.exists(path):
        res = os.path.abspath(path)
        logger.info("The file exists: {}".format(res))
        return res
    else:
        logger.debug("Seaching the default directory: {}".format(
            default_directory))
        path_cand = os.path.join(default_directory, path)
        if os.path.exists(path_cand):
            logger.info("The file exists: {}".format(path_cand))
            return path_cand
        else:
            msg = "Could not find {}".format(path)
            logger.error(msg)
            raise RiddleGeneratorError(msg)


class RiddleProblem(object):

    def __init__(self, problem, answers, logger=DEF_SRG_LOGGER):
        self.problem = problem
        self.answers = answers

    def judge_answer(self, prop_answer, logger=DEF_SRG_LOGGER):
        if prop_answer in self.answers:
            other_answers = {a for a in self.answers if a != prop_answer}
            return True, other_answers
        else:
            return False, set()

    def generate_hints(self, num_characters, logger=DEF_SRG_LOGGER):
        total_len = len(self.problem)
        if not isinstance(num_characters, int):
            raise RiddleGeneratorError("# of characters must be an integer")
        elif 0 < num_characters < total_len - 1:
            rest_num = total_len - num_characters
            hints = [a[:num_characters] + "?" * rest_num for a in self.answers]
            return hints
        else:
            raise RiddleGeneratorError("# of characters is out of range")


class RiddleDictionary(object):

    def __init__(self, dict_path, dict_dir=DEF_DICT_DIR,
                 logger=DEF_SRG_LOGGER):
        self.dict_file = locate_file(dict_path, dict_dir, logger=logger)
        self.dict_name = os.path.basename(self.dict_file)
        self.reader = None
        with open(self.dict_file, encoding="utf-8") as df:
            self.reader = list(csv.DictReader(df))
        logger.info("Successfully read: {}".format(self.dict_file))


class RiddlePreset(object):

    def __init__(self, preset_path, preset_dir=DEF_PRESET_DIR,
                 logger=DEF_SRG_LOGGER):
        self.preset_file = locate_file(preset_path, preset_dir, logger=logger)
        self.preset_name = os.path.basename(self.preset_file)
        self.preset_args = None
        def_preset_file = locate_file(DEF_PRESET_NAME, DEF_PRESET_DIR, logger)
        with open(def_preset_file, encoding="utf-8") as def_pre:
            self.preset_args = json.load(def_pre)
        with open(self.preset_file, encoding="utf-8") as pre:
            new_args = json.load(pre)
            for key, val in new_args.items():
                self.preset_args[key] = val
        logger.info("Successfully read: {}".format(self.preset_file))
        logger.info("Preparing words...")
        self.maindicts = [RiddleDictionary(dict_path=d, logger=logger)
                          for d in self.preset_args["maindicts"]]
        self.subdicts = [RiddleDictionary(dict_path=d, logger=logger)
                         for d in self.preset_args["subdicts"]]
        self.minwordlen = self.preset_args["minwordlen"]
        self.maxwordlen = self.preset_args["maxwordlen"]
        self.problem_words = []
        for maindic in self.maindicts:
            for row in maindic.reader:
                sorted_word = row["sorted_word"]
                self.problem_words.append(sorted_word)
        self.problem2answer = collections.defaultdict(set)
        for dic in itertools.chain(self.maindicts, self.subdicts):
            for row in dic.reader:
                orig_word = row["orig_word"]
                sorted_word = row["sorted_word"]
                self.problem2answer[sorted_word].add(orig_word)
        logger.info("Completed. # of the problems: {}".format(
            len(self.problem_words)))

    def generate_problem(self, logger=DEF_SRG_LOGGER):
        prob_word = random.choice(self.problem_words)
        ans_words = self.problem2answer[prob_word]
        return RiddleProblem(prob_word, ans_words, logger=logger)


def interactive_contest(args, logger=DEF_SRG_LOGGER):
    logger.info("Starts the contest.")
    preset = args.preset
    num_problems = args.num
    preset = RiddlePreset(preset, logger=logger)
    res = {"correct_nohint": 0, "correct_hint": 0, "giveup": 0}
    print("Input your answer for each problem, or")
    print("input one of the following commands:")
    print("* HINT [NUM]: to obtain a hint for the current problem")
    print("* GIVEUP: to give up the current problem")
    print("* EXIT: to abort the contest")
    idxs = itertools.count(1) if num_problems == 0 else range(
        1, num_problems + 1)
    aborted = False
    for prob_idx in idxs:
        if aborted:
            break
        hint_used = False
        print()
        tot = str(num_problems) if num_problems > 0 else "inf"
        print("[Question {cur}/{tot}]".format(cur=prob_idx,
                                              tot=tot))
        prob = preset.generate_problem(logger=logger)
        print("{}".format(prob.problem))
        while True:
            ans = input(">>> ")
            if ans == "GIVEUP":
                res["giveup"] += 1
                print("You gave up the problem. :(")
                print("The answer(s): ", end="")
                print(", ".join(prob.answers))
                break
            elif ans.startswith("HINT"):
                try:
                    _, n0 = ans.split()
                    n = int(n0)
                    hints = prob.generate_hints(n, logger=logger)
                except Exception:
                    print("Error. Check the format and retry.")
                else:
                    print("The hint(s): ", end="")
                    print(", ".join(hints))
                    hint_used = True
            elif ans == "EXIT":
                print("You aborted the contest.")
                aborted = True
                break
            else:
                judge, ws = prob.judge_answer(ans, logger=logger)
                if judge:
                    print("Your answer '{}' is correct! :)".format(ans))
                    print("Other possible answer(s): ", end="")
                    print(", ".join(ws) if ws else "(None)")
                    if hint_used:
                        res["correct_hint"] += 1
                    else:
                        res["correct_nohint"] += 1
                    break
                else:
                    print("Wrong answer. Try again.")
    print()
    print("[Summary]")
    print("Correct (without hints): {}".format(res["correct_nohint"]))
    print("Correct (with hints): {}".format(res["correct_hint"]))
    print("Gave up: {}".format(res["giveup"]))
    print()
    print("Bye! :)")


def main():
    # logging
    logger = DEF_SRG_LOGGER
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        "%(levelname)s: %(name)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # arguments
    parser = argparse.ArgumentParser(
        description="Generating sorting riddles",
        epilog="See '%(prog)s <mode> --help' for details.")
    parser.add_argument("--version", action="version",
                        version="%(progs) " + __version__)
    parser.add_argument("--verbose", "-v", action="count", default=0)
    subparsers = parser.add_subparsers(
        help="Available modes.",
        dest="contest")
    parser_contest = subparsers.add_parser("contest",
                                           help="Let's play!")
    parser_contest.set_defaults(func=interactive_contest)
    parser_contest.add_argument("-p", "--preset",
                                help="the name of " +
                                     "preset file (*.json)",
                                default=DEF_PRESET_NAME)
    parser_contest.add_argument("-n", "--num",
                                help="the number of problems. " +
                                     "< 1 means infinity",
                                default=0,
                                type=int
                                )
    args = parser.parse_args()
    if args.verbose == 1:
        console_handler.setLevel(logging.INFO)
    elif args.verbose >= 2:
        console_handler.setLevel(logging.DEBUG)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
