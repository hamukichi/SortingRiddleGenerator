#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sorting Riddle Generator
"""

__author__ = "Hamukichi (Nombiri)"
__version__ = "0.1.0"
__date__ = "2019-08-03"
__license__ = "MIT License"


import csv
import logging
import os


DEF_DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")
DEF_PRESET_DIR = os.path.join(os.path.dirname(__file__), "presets")
DEF_PRESET_NAME = "default.json"
DEF_SRG_LOGGER = logging.getLogger(__name__)
DEF_SRG_LOGGER.addHandler(logging.NullHandler())


class RiddleGeneratorError(Exception):
    pass


class RiddleDictionary(object):

    def __init__(self, logger=DEF_SRG_LOGGER):
        pass