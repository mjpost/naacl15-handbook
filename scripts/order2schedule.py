#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Generates schedules from properly-formatted order files.
#
# Note: order file must be properly formatted.
#
# Bugs: Workshop chairs do not like to properly format order files

import re
import sys
import codecs
import argparse

PARSER = argparse.ArgumentParser(description="Generates LaTeX schedules from ACLPUB order files")
PARSER.add_argument("workshop", type=str, help="Workshop ID (e.g., papers, WMT14, ...)")
PARSER.add_argument('-basedir', type=str, default='data', help="Location of workshop proceedings tarballs")
args = PARSER.parse_args()


