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
PARSER.add_argument('order_files', nargs='+', help='List of order files')
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


def threedigits(str):
    return '%03d' % (int(str))

class Paper:
    def __init__(self, line, subconf):
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
            self.id = '%s-%s' % (subconf, threedigits(self.id))
            
    def __str__(self):
        return "%s %s" % (id, time)

class Session:
    def __init__(self, line, date):
        (self.time, namestr) = line[2:].split(' ', 1)
        self.date = date
        self.papers = []
        self.desc = None

        (self.name, self.keywords) = handbook.extract_keywords(namestr)
#        print "SESSION", self.time, self.name, self.keywords

        if self.name.find(':') != -1:
            colonpos = self.name.find(':')
            self.desc = self.name[colonpos+2:]
            self.name = self.name[:colonpos]
        # print >> sys.stderr, "LINE %s NAME %s DESC %s" % (line, self.name, self.desc)

    def __str__(self):
        return "SESSION [%s/%s] %s %s" % (self.date, self.time, self.name, self.desc)

    def add_paper(self,paper):
        self.papers.append(paper)

    def num(self):
        # strip off the last char (A, B, C, D, etc)
        # turns, e.g., "Session 1A" into "1"
        return self.name.split(' ')[-1][:-1]

    def chair(self):
        """Returns the (first name, last name) of the chair, if found in a %chair keyword"""
        
        if self.keywords.has_key('chair'):
            fullname = self.keywords['chair']
            if ',' in fullname:
                names = fullname.split(', ')
                return (names[1].strip(), names[0].strip())
            else:
                # This is just a heuristic, assuming the first name is one word and the last
                # name is 1+ words
                names = fullname.split(' ', 1)
                return (names[0].strip(), names[1].strip())
        else:
            return ('', '')

# List of dates
dates = []
schedule = defaultdict(defaultdict)
sessions = defaultdict()
session_times = defaultdict()

for file in args.order_files:
    subconf_name = file.split('/')[1]
    for line in open(file):
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

            if "poster" in title.lower() or "demo" in title.lower():
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

            sessions[session_name].add_paper(Paper(line, subconf_name))

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
    if "--" in time:
        return '--'.join(map(lambda x: minus12(x), time.split('--')))

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
                print >>out, '  {%s}' % (session.desc)

#            print "START", start, "STOP", stop, day, sessions[0]
            times = [minus12(p.time.split('--')[1]) for p in sessions[0].papers]
            for paper_num in range(num_papers):
                if paper_num > 0:
                    print >>out, ' \\hline'
                print >>out, '  \\marginnote{\\rotatebox{90}{%s}}[2mm]' % (times[paper_num])
                papers = [session.papers[paper_num] for session in sessions]
                print >>out, '  ', ' & '.join(['\\papertableentry{%s}' % (p.id) for p in papers])
                print >>out, '\\\\'

            print >>out, '\\end{ThreeSessionOverview}\n'

            # Print the papers
            print >>out, '\\newpage'
            print >>out, '\\section*{Parallel Session %s}' % (session_num)
            for i, session in enumerate(sessions):
                chair = session.chair()
                print >>out, '{\\bfseries\\large %s: %s}\\\\' % (session.name, session.desc)
                print >>out, '\\Track%cLoc\\hfill\\sessionchair{%s}{%s}' % (chr(i + 65),chair[0],chair[1])
                for paper in session.papers:
                    print >>out, '\\paperabstract{\\day}{%s}{}{}{%s}' % (paper.time, paper.id)
                print >>out, '\\clearpage'

        else:
            session = event[0]
            # Poster session
            print >>out, '{\\section{%s}' % (session.name)
            print >>out, '{\\setheaders{%s}{\\daydateyear}' % (session.name)
            print >>out, '%s\\\\' % (minus12(session.time))
            for paper in session.papers:
                print >>out, '\\posterabstract{%s}' % (paper.id)

        print >>out, '\n'

    out.close()
