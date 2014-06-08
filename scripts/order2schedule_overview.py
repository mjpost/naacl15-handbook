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
session_times = defaultdict()

for line in sys.stdin:
    line = line.rstrip()

    # print "LINE", line

    if line.startswith('*'):
        day, date, year = line[2:].split(', ')
        if not (day, date, year) in dates:
            dates.append((day, date, year))

    elif line.startswith('='):
        session_name = line[2:]

    elif line.startswith('+'):
        timerange, title = line[2:].split(' ', 1)
        session_name = None

        schedule[(day, date, year)][timerange] = title

    elif re.match(r'\d+', line):
        """For the overview, we don't print sessions or papers, but we do need to look at
        oral presentations in order to determine the time range of the session (if any applies)"""
        if re.match(r'\d+:\d+', line.split(' ')[1]):
            if session_name is None:
                print "* WARNING: paper without a session name"
                continue

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

# Take all the sessions and place them at their time
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

def minus12(time):
    hours, minutes = time.split(':')
    if hours.startswith('0'):
        hours = hours[1:]
    if int(hours) >= 13:
        hours = `int(hours) - 12`

    return '%s:%s' % (hours, minutes)

for date in dates:
    day, num, year = date
    out = open(os.path.join(args.output_dir, '%s.tex' % (day)), 'w')
    print >>out, '\\section*{Overview}'
    print >>out, '\\renewcommand{\\arraystretch}{1.2}'
    print >>out, '\\begin{SingleTrackSchedule}'
    for key, val in sorted(schedule[date].iteritems(), cmp=sort_times):
        start, stop = key.split('--')

        if isinstance(val, list) and re.search(r':', val[0]):
            sessions = [x for x in val]
            title = sessions[0].split(':')[0][:-1]
            print >>out, '  %s & -- & %s &' % (minus12(start), minus12(stop))
            print >>out, '  \\begin{tabular}{|p{.6in}|p{.6in}|p{.6in}|p{.6in}|p{.6in}|}'
            print >>out, '    \\multicolumn{5}{l}{{\\bfseries %s}}\\\\\\hline' % (title)
            print >>out, ' & '.join([x.split(': ')[1] for x in sessions]), '\\\\'
            print >>out, '  \\hline\\end{tabular} \\\\'

        else:
            print >>out, '  %s & -- & %s &' % (minus12(start), minus12(stop))
            print >>out, '  {\\bfseries %s} \\hfill (\\UnknownLoc)' % (val)
            print >>out, '  \\\\'

    print >>out, '\\end{SingleTrackSchedule}'
    out.close()
