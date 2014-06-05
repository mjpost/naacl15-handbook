#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script reads all the metadata and creates a bibtex file that contains
# all the information we need for the conference handbook. Unlike the bibtex
# file on the CDROM in the proceedings, bibtex labels correspond to submission
# numbers.

# Usage

# Written by Ulrich Germann, May 2012.

from paper_info import *
import sys, os, unicodedata, codecs
import re

fdir = sys.argv[1] # i.e., $ACLPUB_ROOT/final
tag  = sys.argv[2] # e.g., main, demos, ws1, ...

try:
    os.makedirs("auto/%s" % (tag))
except:
    pass

try:
    os.makedirs("auto/abstracts")
except:
    pass

def escape(str):
    str = str.replace('%','\%').replace('~','{\\textasciitilde}')
    str = re.sub(r'([^$])\^(.*?) ', r'\1$^\2$ ', str)
    return str

paper_ids = [int(n) for n in os.listdir(fdir)]
BIBFILE   = open("auto/"+tag+"/papers.bib",'w')
for n in paper_ids:
    n = int(n)
    p = Paper("%s/%d/%d_metadata.txt" % (fdir, n, n))
    author = " and ".join(["%s, %s" % (a.last, a.first) for a in p.authors])
    sortname = ''.join([c for c in unicodedata.normalize('NFD', unicode(author))
                        if unicodedata.category(c) != 'Mn'])
    #print author.encode("utf-8")
    #print sortname.encode("utf-8")
    print >>BIBFILE, "@INPROCEEDINGS{%s-%03d," % (tag, int(p.id))
    print >>BIBFILE, "   AUTHOR = {%s}," % author.encode("utf-8")
    print >>BIBFILE, "   SORTNAME = {%s}," % sortname.encode("utf-8")
    print >>BIBFILE, "   TITLE = {%s}}" % p.long.encode("utf-8")
    ABS = open("auto/abstracts/%s-%03d.tex" % (tag, n),'w')
    print >>ABS, escape(p.abstract).encode("utf-8")
    
