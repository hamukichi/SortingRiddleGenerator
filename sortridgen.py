#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sorting Riddle Generator
"""

__author__ = "Hamukichi (Nombiri)"
__version__ = "0.3.0-alpha"
__date__ = "2019-08-12"
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
import re


ACCEPTABLE_FOREIGN_INPUT_FORMATS = ["mecab-naist-jdic", "sort_nazonazo"]
ACCEPTABLE_FOREIGN_OUTPUT_FORMATS = ["sort_nazonazo"]
PROG_ROOT_DIR = pathlib.Path(__file__).parent.resolve()
DEF_DICT_DIR = os.path.join(PROG_ROOT_DIR, "dictionaries")
DEF_PRESET_DIR = os.path.join(PROG_ROOT_DIR, "presets")
DEF_PRESET_NAME = "default.json"
DEF_SRG_LOGGER = logging.getLogger(__name__)
DEF_SRG_LOGGER.addHandler(logging.NullHandler())
DEF_WORD_PTN = re.compile(r"[a-zあ-んア-ン]*")


class RiddleGeneratorError(Exception):
    pass


def conv_to_foreign_dic(in_path, out_path, format, out_enc=None,
                        min_word_len=1, max_word_len=1024,
                        logger=DEF_SRG_LOGGER):
    if format not in ACCEPTABLE_FOREIGN_OUTPUT_FORMATS:
        raise RiddleGeneratorError(
            "The format {} cannot be accepted.".format(format))
        logger.info("Reads " + in_path + " (format = CSV)")
    if format == "sort_nazonazo":
        if out_enc is None:
            out_enc = "utf-8"
        with open(in_path, newline="",
                  encoding="utf-8") as in_csv, open(out_path,
                                                    encoding=out_enc,
                                                    mode="w") as out_f:
            in_reader = csv.DictReader(in_csv)
            for row in in_reader:
                orig_word = row["orig_word"]
                sorted_word = row["sorted_word"]
                if min_word_len <= orig_word <= max_word_len:
                    print(orig_word, sorted_word, file=out_f)
    logger.info("Successfully generated " + out_path)


def conv_from_foreign_dic(in_path, out_path, format, in_enc=None,
                          word_ptn=DEF_WORD_PTN, logger=DEF_SRG_LOGGER):
    if format not in ACCEPTABLE_FOREIGN_INPUT_FORMATS:
        raise RiddleGeneratorError(
            "The format {} cannot be accepted.".format(format))
    logger.info("Reads " + in_path + " (format = " + format + ")")
    if format == "mecab-naist-jdic":
        if in_enc is None:
            in_enc = "euc-jp"
        with open(in_path, newline="",
                  encoding=in_enc) as in_csv, open(out_path,
                                                   newline="",
                                                   encoding="utf-8",
                                                   mode="w") as out_csv:
            in_reader = csv.reader(in_csv)
            out_writer = csv.DictWriter(
                out_csv, fieldnames=["orig_word", "sorted_word"])
            out_writer.writeheader()
            for row in in_reader:
                is_match = word_ptn.fullmatch(row[11])
                if row[4] == "名詞" and row[5] == "一般" and is_match:
                    orig_word = row[11]
                    sorted_word = "".join(sorted(orig_word))
                    out_writer.writerow({"orig_word": orig_word,
                                         "sorted_word": sorted_word})
    elif format == "sort_nazonazo":
        if in_enc is None:
            in_enc = "utf-8"
        with open(in_path, newline="",
                  encoding=in_enc) as in_dic, open(out_path,
                                                   newline="",
                                                   encoding="utf-8",
                                                   mode="w") as out_csv:
            out_writer = csv.DictWriter(
                out_csv, fieldnames=["orig_word", "sorted_word"])
            out_writer.writeheader()
            for line in in_dic:
                try:
                    orig_word, sorted_word = line.rstrip("\n").split()
                except Exception:
                    continue
                else:
                    out_writer.writerow({"orig_word": orig_word,
                                         "sorted_word": sorted_word})
    logger.info("Successfully generated " + out_path)


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
                if self.minwordlen <= len(sorted_word) <= self.maxwordlen:
                    self.problem_words.append(sorted_word)
        self.problem2answer = collections.defaultdict(set)
        for dic in itertools.chain(self.maindicts, self.subdicts):
            for row in dic.reader:
                orig_word = row["orig_word"]
                sorted_word = row["sorted_word"]
                if self.minwordlen <= len(sorted_word) <= self.maxwordlen:
                    self.problem2answer[sorted_word].add(orig_word)
        logger.info("Completed. # of the problems: {}".format(
            len(self.problem_words)))

    def generate_problem(self, logger=DEF_SRG_LOGGER):
        prob_word = random.choice(self.problem_words)
        ans_words = self.problem2answer[prob_word]
        return RiddleProblem(prob_word, ans_words, logger=logger)


def _interactive_contest(args, logger=DEF_SRG_LOGGER):
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


def _converter(args, logger=DEF_SRG_LOGGER):
    conv_from_foreign_dic(in_path=args.in_path, out_path=args.out_path,
                          format=args.format, in_enc=args.encoding,
                          logger=logger)


def _inv_converter(args, logger=DEF_SRG_LOGGER):
    conv_to_foreign_dic(in_path=args.in_path, out_path=args.out_path,
                        format=args.format, out_enc=args.encoding,
                        min_word_len=args.minwordlen,
                        max_word_len=args.maxwordlen,
                        logger=logger)


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
    # arguments (general)
    parser = argparse.ArgumentParser(
        description="Generating sorting riddles",
        epilog="See '%(prog)s <mode> --help' for details.")
    parser.add_argument("--version", action="version",
                        version="%(progs) " + __version__)
    parser.add_argument("--verbose", "-v", action="count", default=0)
    subparsers = parser.add_subparsers(
        help="Available modes.",
        dest="mode")
    # arguments (contest)
    parser_contest = subparsers.add_parser("contest",
                                           help="to start a contest")
    parser_contest.set_defaults(func=_interactive_contest)
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
    # arguments (convert)
    parser_convert = subparsers.add_parser("convert",
                                           help="to generate a dictionary " +
                                           "(*.csv) from a foreign file")
    parser_convert.set_defaults(func=_converter)
    parser_convert.add_argument("format",
                                help="the format of the input file",
                                choices=ACCEPTABLE_FOREIGN_INPUT_FORMATS)
    parser_convert.add_argument("in_path",
                                help="the path to the input file")
    parser_convert.add_argument("out_path",
                                help="the path to the output (*.csv)")
    parser_convert.add_argument("-e", "--encoding",
                                help="the encoding of the input file")
    # arguments (invconv)
    parser_invconv = subparsers.add_parser("invconv",
                                           help="to generate a foreign " +
                                                "file from a dictionary " +
                                                " (*.csv)")
    parser_invconv.set_defaults(func=_inv_converter)
    parser_invconv.add_argument("format",
                                help="the format of the output file",
                                choices=ACCEPTABLE_FOREIGN_OUTPUT_FORMATS)
    parser_invconv.add_argument("in_path",
                                help="the path to the input file (*.csv)")
    parser_invconv.add_argument("out_path",
                                help="the path to the output file")
    parser_invconv.add_argument("-e", "--encoding",
                                help="the encoding of the output file")
    parser_invconv.add_argument("-m", "--minwordlen",
                                help="the minimum length of words",
                                type=int,
                                default=1)
    parser_invconv.add_argument("-M", "--maxwordlen",
                                help="the maximum length of words",
                                type=int, default=1024)
    # parse
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
