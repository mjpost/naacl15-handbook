#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Matt Post, June 2014

"""
Generates the daily overviews for the main conference schedule. Amalgamates multiple order
iles containing difference pieces of the schedule and outputs a schedule for each day,
rooted in an optionally-supplied directory.

Usage:

 cat {papers,shortpapers,demos,tacl}/proceedings/order | order2schedule_overview.py auto/papers

"""

import re
import os
import sys
import argparse
from collections import defaultdict

PARSER = argparse.ArgumentParser(description="Generate overview schedules for *ACL handbooks")
PARSER.add_argument("-output_dir", dest="output_dir", default="auto/papers")
args = PARSER.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

# List of dates
dates = []
schedule = defaultdict(defaultdict)

for line in sys.stdin:
    line = line.rstrip()

    print "LINE", line


    if line.startswith('*'):
        day, date, year = line[2:].split(', ')
        if not (day, date, year) in dates:
            dates.append((day, date, year))

    elif line.startswith('='):
        session_name = line[2:]
        session_start = None
        session_stop = None

    elif line.startswith('+'):
        timerange, title = line[2:].split(' ', 1)

        schedule[(day, date, year)][timerange] = title

    elif re.match(r'\d+', line):
        """For the overview, we don't print sessions or papers, but we do need to look at
        oral presentations in order to determine the time range of the session (if any applies)"""
        if re.match(r'\d+:\d+', line.split(' ')[1]):
            timerange = line.split(' ')[1]
            start, stop = timerange.split('--')

            if session_start:
                timerange = '%s--%s' % (session_start, session_stop)
                schedule[(day, date, year)][timerange].pop(-1)
                print "* DELETING", timerange, session_name
            else:
                session_start = start

            session_stop = stop
            timerange = '%s--%s' % (session_start, session_stop)
            if not schedule[(day, date, year)].has_key(timerange):
                schedule[(day, date, year)][timerange] = []
            schedule[(day, date, year)][timerange].append(session_name)
            print "* CREATING", timerange, session_name

def sort_times(a, b):
    ahour, amin = a[0].split('--')[0].split(':')
    bhour, bmin = b[0].split('--')[0].split(':')
    if ahour == bhour:
        return cmp(int(amin), int(bmin))
    return cmp(int(ahour), int(bhour))

for date in dates:
    print date

    for key,val in sorted(schedule[date].iteritems(), cmp=sort_times):
        print '  ', key, val
