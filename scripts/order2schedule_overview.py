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

import re, os
import sys, csv
import argparse
import acl
from collections import defaultdict

PARSER = argparse.ArgumentParser(description="Generate overview schedules for *ACL handbooks")
PARSER.add_argument("-output_dir", dest="output_dir", default="auto/papers")
PARSER.add_argument("-location_file", default='input/room_assignments.csv', type=str, help="File path for CSV locations")
args = PARSER.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

locations = {}
if args.location_file is not None:
    for row in csv.DictReader(open(args.location_file)):
        locations[row['event']] = '\\\\%sLoc' % (row['event'])

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
        str = line[2:]
        time_range, session_name = str.split(' ', 1)
        sessions[session_name] = (day, date, year, time_range)

    elif line.startswith('+') or line.startswith('!'):
        timerange, title = line[2:].split(' ', 1)
        title, keys = acl.extract_keywords(title)
        if keys.has_key('by'):
            title = "%s (%s)" % (title.strip(), keys['by'])
        session_name = None

        schedule[(day, date, year)][timerange] = title

# Take all the sessions and place them at their time
for session in sorted(sessions.keys()):
    day, date, year, timerange = sessions[session]
#    print >> sys.stderr, "SESSION", session, day, date, year, timerange
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
    path = os.path.join(args.output_dir, '%s.tex' % (day))
    out = open(path, 'w')
    print >> sys.stderr, "Writing file", path
    print >>out, '\\section*{Overview}'
    print >>out, '\\renewcommand{\\arraystretch}{1.2}'
    print >>out, '\\begin{SingleTrackSchedule}'
    for key, val in sorted(schedule[date].iteritems(), cmp=sort_times):
        start, stop = key.split('--')

        def sessioncode(name):
            """Session 9C: Machine Translation -> Session 9C"""
            if name.find(':') == -1:
                return name
            else:
                return name[:name.find(':')]

        def sessiontitle(name):
            """10:40--11:40 Session 9C: Machine Translation -> Machine Translation"""
            name = name[name.find(' ')+1:]
            if name.find(':') == -1:
                return name
            else:
                return name[name.find(':')+2:]

        if isinstance(val, list) and re.search(r':', val[0]):
            sessions = [x for x in val]

            # turn "Session 9A" to "Session 9"
            title = sessioncode(sessions[0])[:-1]
            num_parallel_sessions = len(sessions)
            locations = ['\emph{\Track%cLoc}' % (chr(65+x)) for x in range(num_parallel_sessions)]
            # column width in inches
            width = 3.0 / num_parallel_sessions
            print >>out, '  %s & -- & %s &' % (minus12(start), minus12(stop))
            print >>out, '  \\begin{tabular}{|%s|}' % ('|'.join(['p{%.1fin}' % width for x in range(num_parallel_sessions)]))
            print >>out, '    \\multicolumn{%d}{l}{{\\bfseries %s}}\\\\\\hline' % (num_parallel_sessions,title)
            print >>out, ' & '.join([sessiontitle(x) for x in sessions]), '\\\\'
            print >>out, ' & '.join(locations), '\\\\'
            print >>out, '  \\hline\\end{tabular} \\\\'

        else:
            print >>out, '  %s & -- & %s &' % (minus12(start), minus12(stop))
#            loc = locations.get(val, "\\UnknownLoc")
            loc = "\\UnknownLoc"
            print >>out, '  {\\bfseries %s} \\hfill (%s)' % (val, loc)
            print >>out, '  \\\\'

    print >>out, '\\end{SingleTrackSchedule}'
    out.close()
