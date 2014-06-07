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

def time_min(a, b):
    ahour, amin = a.split(':')
    bhour, bmin = b.split(':')
    if ahour == bhour:
        if amin < bmin:
            return a
        elif amin > bmin:
            return b
        else:
            return a
    elif ahour < bhour:
        return a
    else:
        return b

def time_max(a, b):
    if time_min(a, b) == a:
        return b
    return a

# List of dates
dates = []
schedule = defaultdict(defaultdict)
sessions = defaultdict()

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

            if sessions.has_key(session_name):
                old_start, old_stop = sessions[session_name][3].split('--')
                if old_start != start or old_stop != stop:
                    old_timerange = '%s--%s' % (old_start, old_stop)
                    new_timerange = '%s--%s' % (time_min(old_start, start), time_max(old_stop, stop))

                    sessions[session_name] = (day, date, year, new_timerange)

            else:
                sessions[session_name] = (day, date, year, timerange)

for session in sorted(sessions.keys()):
    day, date, year, timerange = sessions[session]
    if not schedule[(day, date, year)].has_key(timerange):
        schedule[(day, date, year)][timerange] = []
    schedule[(day, date, year)][timerange].append(session)

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
