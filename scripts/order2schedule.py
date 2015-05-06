#!/usr/bin/env python 
# -*- coding: utf-8 -*-

"""
Generates the daily schedules for the main conference schedule. Amalgamates multiple order
files containing difference pieces of the schedule and outputs a schedule for each day,
rooted in an optionally-supplied directory.

Note: order file must be properly formatted.

Bugs: Workshop and program chairs do not like to properly format order files.

Usage: 

    cat data/{papers,shortpapers,demos,srw}/order | python order2schedule.py
"""

import re, os
import sys, csv
import argparse
import handbook
from collections import defaultdict

PARSER = argparse.ArgumentParser(description="Generate schedules for *ACL handbooks")
PARSER.add_argument("-output_dir", dest="output_dir", default="auto/papers")
PARSER.add_argument("-location_file", default='input/room_assignments.csv', type=str, help="File path for CSV locations")
args = PARSER.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

locations = handbook.load_location_file(args.location_file)

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


def threedigits(str):
    return '%03d' % (int(str))

class Paper:
    def __init__(self, line):
        self.id, rest = line.split(' ', 1)
        if re.match(r'^\d+', rest) is not None:
            self.time, comment = rest.split(' ', 1)
        else:
            self.time = None
            comment = rest

        if self.id.find('/') != -1:
            tokens = self.id.split('/')
            self.id = '%s-%s' % (tokens[1].lower(), threedigits(tokens[0]))
        else:
            self.id = 'papers-%s' % (threedigits(self.id))
            
class Session:
    def __init__(self, line, date):
        (self.time, self.name) = line[2:].split(' ', 1)
        self.date = date
        self.papers = []

        if self.name.find(':') == -1:
            self.code = None
        else:
            self.code = self.name[:self.name.find(':')]
            self.name = self.name[self.name.find(':')+2:]

    def add_paper(self,paper):
        self.papers.append(paper)

    def num(self):
        # strip off the last char (A, B, C, D, etc)
        return self.code[:-1]
        
    def title(self):
        return self.name


# List of dates
dates = []
schedule = defaultdict(defaultdict)
sessions = defaultdict()
session_times = defaultdict()

for line in sys.stdin:
    line = line.rstrip()

    # print "LINE", line

    if line.startswith('*'):
        # This sets the day
        day, date, year = line[2:].split(', ')
        if not (day, date, year) in dates:
            dates.append((day, date, year))

    elif line.startswith('='):
        # This names a parallel session that runs at a certain time
        str = line[2:]
        time_range, session_name = str.split(' ', 1)
        sessions[session_name] = Session(line, (day, date, year))

    elif line.startswith('+'):
        # This names an event that takes place at a certain time
        timerange, title = line[2:].split(' ', 1)

        if "poster" in title.lower():
            session_name = title
            sessions[session_name] = Session(line, (day, date, year))

    elif re.match(r'^\d+', line) is not None:
        id, rest = line.split(' ', 1)
        if re.match(r'^\d+:\d+-+\d+:\d+', rest) is not None:
            title = rest.split(' ', 1)
        else:
            title = rest

        if not sessions.has_key(session_name):
            sessions[session_name] = Session("= %s %s" % (timerange, session_name), (day, date, year))

        sessions[session_name].add_paper(Paper(line))

# Take all the sessions and place them at their time
for session in sorted(sessions.keys()):
    day, date, year = sessions[session].date
    timerange = sessions[session].time
#    print >> sys.stderr, "SESSION", session, day, date, year, timerange
    if not schedule[(day, date, year)].has_key(timerange):
        schedule[(day, date, year)][timerange] = []
    schedule[(day, date, year)][timerange].append(sessions[session])

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

# Now iterate through the combined schedule, printing, printing, printing.
# Write a file for each date. This file can then be imported and, if desired, manually edited.
for date in dates:
    day, num, year = date
    path = os.path.join(args.output_dir, '%s.tex' % (day))
    out = open(path, 'w')
    print >> sys.stderr, "Writing to file", path
    for timerange, event in sorted(schedule[date].iteritems(), cmp=sort_times):
        start, stop = timerange.split('--')

        if isinstance(event, list) and len(event) > 1:
            # Multiple events at this time -- a set of parallel sessions!
            sessions = [x for x in event]

            session_num = sessions[0].num()

            # Print the Session overview (single-page at-a-glance grid)
            print >>out, '\\clearpage'
            print >>out, '\\setheaders{Parallel Session %s}{\\daydateyear}' % (session_num)
            print >>out, '\\begin{ThreeSessionOverview}{Parallel Session %s}{\daydateyear}' % (session_num)
            num_papers = len(sessions[0].papers)
            for session in sessions:
                print >>out, '  {%s}' % (session.title())

            times = [p.time.split('--')[1] for p in sessions[0].papers]
            for paper_num in range(num_papers):
                print >>out, '  \\marginnote{\\rotatebox{90}{%s}}[2mm]' % (times[paper_num])
                papers = [session.papers[paper_num] for session in sessions]
                print >>out, '  ', ' & '.join(['\\papertableentry{%s}' % (p.id) for p in papers])
                print >>out, ' \\\\\\hline'

            print >>out, '\\end{ThreeSessionOverview}\n'

            # Print the papers
            print >>out, '\\newpage'
            print >>out, '\\section*{Parallel Session %s}' % (session_num)
            for i, session in enumerate(sessions):
                print >>out, '{\\bfseries\\large %s: %s}\\\\' % (session.code, session.title())
                print >>out, '\\Track%cLoc\\hfill\\sessionchair{}{}' % (chr(i + 65))
                for paper in session.papers:
                    print >>out, '\\paperabstract{\\day}{%s}{}{}{%s}' % (paper.time, paper.id)
                print >>out, '\\clearpage'

    out.close()
