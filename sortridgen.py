#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sorting Riddle Generator
"""

__author__ = "Hamukichi (Nombiri)"
__version__ = "0.1.0"
__date__ = "2019-08-03"
__license__ = "MIT License"


import collections
import csv
import itertools
import json
import logging
import os
import random


DEF_DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")
DEF_PRESET_DIR = os.path.join(os.path.dirname(__file__), "presets")
DEF_PRESET_NAME = "default.json"
DEF_SRG_LOGGER = logging.getLogger(__name__)
DEF_SRG_LOGGER.addHandler(logging.NullHandler())


class RiddleGeneratorError(Exception):
    pass


def locate_file(path, default_directory, logger=DEF_SRG_LOGGER):
    if os.path.exists(path):
        res = os.path.abspath(path)
        logger.info("The file exists: {}".format(res))
        return res
    else:
        logger.info("Seaching the default directory: {}".format(
            default_directory))
        path_cand = os.path.join(default_directory, path)
        if os.path.exists(path_cand):
            res = os.path.abspath(path)
            logger.info("The file exists: {}".format(res))
            return res
        else:
            msg = "Could not find {}".format(path)
            logger.error(msg)
            raise RiddleGeneratorError(msg)


class RiddleDictionary(object):

    def __init__(self, dict_path, dict_dir=DEF_DICT_DIR,
                 logger=DEF_SRG_LOGGER):
        self.dict_file = locate_file(dict_path, dict_dir, logger=logger)
        self.dict_name = os.path.basename(self.dict_file)
        self.reader = None
        with open(self.dict_file, encoding="utf-8") as df:
            self.reader = csv.DictReader(df)
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
        self.maindics = [RiddleDictionary(dict_path=d, logger=logger)
                         for d in self.preset_args["maindics"]]
        self.subdics = [RiddleDictionary(dict_path=d, logger=logger)
                        for d in self.preset_args["subdics"]]
        self.minwordlen = self.preset_args["minwordlen"]
        self.maxwordlen = self.preset_args["maxwordlen"]
        self.problem_words = set()
        for maindic in self.maindics:
            for row in maindic.reader:
                sorted_word = row["sorted_word"]
                self.problem_words.add(sorted_word)
        self.problem2answer = collections.defaultdict(set)
        for dic in itertools.chain(self.maindics, self.subdics):
            for row in dic.reader:
                orig_word = row["orig_word"]
                sorted_word = row["sorted_word"]
                self.problem2answer[sorted_word].add(orig_word)
        logger.info("Completed.")
        logger.info("# of the problems: {}".format(len(self.problem_words)))
