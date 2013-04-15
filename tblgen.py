#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright 2013 Zack Weinberg <zackw@panix.com> and other contributors.
#
# Copying and distribution of this program, with or without
# modification, is permitted in any medium without royalty provided
# the copyright notice and this notice are preserved.  It is offered
# as-is, without any warranty.

# Note to contributors: Unlike scansys.py, this program only needs
# to work with Python 2.7 and may grow dependencies on third-party
# libraries in the future (e.g. an HTML generator of some sort).
# Some code is functionally duplicated from scansys.py but with the
# compatibility contortions removed; this is why there is no shared
# support library.

from __future__ import unicode_literals

import errno
import itertools
import os
import re
import sys

from genshi.template import TemplateLoader
from genshi.core import TEXT
from genshi.output import HTMLSerializer
from string import punctuation as _punctuation

# Sort a list of pathnames, ASCII case-insensitively.  All
# one-component pathnames are sorted ahead of all longer pathnames;
# within a group of multicomponent pathnames with the same leading
# component, all two-component pathnames are sorted ahead of all
# longer pathnames; and so on, recursively.

def hsortkey(h):
    def hsortkey_r(hd, *tl):
        if len(tl) == 0: return (0, hd)
        return (1, hd) + hsortkey_r(*tl)

    segs = h.lower().replace("\\", "/").split("/")
    return hsortkey_r(*segs)

def sorthdr(hs):
    return sorted(hs, key=hsortkey)

# hat tip to http://code.activestate.com/recipes/285264-natural-string-sorting/
_natsort_split_re = re.compile(r'(\d+|\D+)')
def natsort_key(s):
    def try_int(s):
        try: return int(s)
        except: return s.lower()
    return tuple(try_int(c) for c in _natsort_split_re.findall(s))

class Dataset(object):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0:
            other = args[0]
            self.items = other.items
            self.label = other.label
            self.version = other.version
            self.compiler = "<merged>"
            self.category = other.category
            self.sequence = other.sequence
            self.catkey = other.catkey
            self.labelkey = other.labelkey
            self.verskey = other.verskey
        else:
            assert len(args) == 0
            self.items = kwargs['items']
            self.label = kwargs['label']
            self.version = kwargs['version']
            self.compiler = kwargs['compiler']
            self.category = kwargs['category']
            self.sequence = kwargs['sequence']
            # "embedded X" sorts immediately after X; otherwise,
            # categories are case-insensitive alphabetical
            if self.category.startswith("embedded "):
                self.catkey = (self.category[9:].lower(), 1)
            else:
                self.catkey = (self.category.lower(), 0)
            # numbers within labels are sorted numerically
            self.labelkey = natsort_key(self.label)
            self.verskey = natsort_key(self.version)

    @classmethod
    def from_file(cls, fname):
        label = fname
        if fname.startswith("b-") or fname.startswith("h-"):
            label = label[2:]
        if fname.endswith(".txt"):
            label = label[:-4]
        label = label.replace("-", " ")
        sequence = 50
        category = "Uncategorized"
        compiler = "unknown"
        version = "unknown"

        items = {}
        with open(fname, "rU") as fp:
            for line in fp:
                line = line.strip()
                if line == "" or line[0] == "#": continue
                if line[0] == ":":
                    if line.startswith(":label "):
                        label = line[7:]
                    elif line.startswith(":version "):
                        version = line[9:]
                    elif line.startswith(":category "):
                        category = line[10:]
                    elif line.startswith(":compiler "):
                        compiler = line[10:]
                    elif line.startswith(":sequence "):
                        sequence = int(line[10:])
                    else:
                        raise RuntimeError("{}: unknown directive-line {0!r}"
                                           .format(fname, line))
                    continue

                line = line.replace('\\', '/')
                if line[0] in _punctuation:
                    p = line[0]
                    l = line[1:]
                    if p == '!': p = 'B'
                    elif p == '%': p = 'P'
                    else:
                        raise RuntimeError("{}: {}: unsupported tag symbol: {}"
                                           .format(fname, l, p))

                else:
                    p = 'Y'
                    l = line
                if l in items:
                    raise RuntimeError("{}: duplicate header-line {0!r}"
                                       .format(fname, line))
                items[l] = p

        return cls(items=items,
                   label=label,
                   version=version,
                   category=category,
                   compiler=compiler,
                   sequence=sequence)

    def merge_compiler(self, other):
        def merge_compiler_1(mine, theirs):
            assert mine != '' or theirs != ''
            if mine == theirs:
                return mine
            new = ''
            if 'Y' in mine or 'Y' in theirs: new += 'Y'
            if 'P' in mine or 'P' in theirs: new += 'P'
            if 'B' in mine or 'B' in theirs: new += 'B'
            if ('N' in mine or 'N' in theirs
                or '' == mine or '' == theirs): new += 'N'
            return new

        assert self.label == other.label and self.version == other.version
        allh = frozenset(itertools.chain(self.items.iterkeys(),
                                         other.items.iterkeys()))
        mergeh = {}
        for h in allh:
            mine   = self.items.get(h, '')
            theirs = other.items.get(h, '')
            mergeh[h] = merge_compiler_1(mine, theirs)
        self.items = mergeh

    def maybe_merge_versions(self, other):
        assert self.label == other.label and self.version != other.version
        assert self.verskey < other.verskey

        if self.items != other.items:
            return False

        if "–" in self.version:
            (before, dash, after) = self.version.partition("–")
            self.version = before + "–" + other.version
        else:
            self.version = self.version + "–" + other.version
        return True

    # We don't use rich comparisons for this class because (a) it'd be
    # harder to write, and (b) sort() doesn't seem to honor them.
    def __cmp__(self, other):
        return (cmp(self.sequence, other.sequence) or
                cmp(self.catkey, other.catkey) or
                cmp(self.labelkey, other.labelkey) or
                cmp(self.verskey, other.verskey) or
                cmp(self.compiler, other.compiler) or
                cmp(self.items, other.items))

    # delegate item accessors
    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __contains__(self, x):
        return x in self.items

    def __getitem__(self, x):
        return self.items[x]

    def get(self, x, d=None):
        return self.items.get(x, d)

def load_datasets(dirname):
    datasets = []
    rv = 0
    try:
        files = os.listdir(dirname)
    except EnvironmentError, e:
        sys.stderr.write("{}: {}\n".format(e.filename, e.strerror))
        rv = 1;
        return rv, datasets

    for fname in os.listdir(dirname):
        if not (fname.startswith("b-") or fname.startswith("h-")):
            continue
        try:
            datasets.append(Dataset.from_file(os.path.join(dirname, fname)))
        except EnvironmentError, e:
            # silently skip directories
            # report all other errors and continue
            if e.errno != errno.EISDIR:
                sys.stderr.write("{}: {}\n".format(e.filename,
                                                   e.strerror))
                rv = 1

    return rv, datasets

def preprocess_osgrp(osgroup):
    assert len(frozenset(os.label for os in osgroup)) == 1

    versions = {}
    for os in osgroup:
        merged = versions.get(os.version, None)
        if merged is not None:
            merged.merge_compiler(os)
        else:
            versions[os.version] = Dataset(os)
    verlist = versions.values()
    verlist.sort()

    nverlist = []
    one = verlist[0]
    for two in verlist[1:]:
        if not one.maybe_merge_versions(two):
            nverlist.append(one)
            one = two
    nverlist.append(one)
    return nverlist

def preprocess(datasets):

    # separate standards-sets from os-sets, cluster os-sets by label
    osgrps = {}
    stds = []
    for d in datasets:
        if d.category == "standard":
            stds.append(d)
        else:
            other = osgrps.get(d.label)
            if other is not None:
                other.append(d)
            else:
                osgrps[d.label] = [d]
    stds.sort()

    # compute version ranges and compiler dependencies
    oses = []
    for osgroup in osgrps.itervalues():
        oses.extend(preprocess_osgrp(osgroup))
    oses.sort()

    # cluster oses by category
    class OsCat(list):
        def __init__(self, name):
            self.name = name
    oscats = []
    curcat = oses[0].category
    curcatlist = OsCat(curcat)
    for os in oses:
        if os.category != curcat:
            oscats.append(curcatlist)
            curcat = os.category
            curcatlist = OsCat(curcat)
        curcatlist.append(os)
    oscats.append(curcatlist)

    return oscats, stds

# If someone can suggest a more elegant, or at least less repetitive,
# way to write this transform, I am all ears.
_wsre = re.compile(r'\s+', re.UNICODE)
def collapse_ws_xml(stream):
    wsre = _wsre
    tqueue_data = None
    tqueue_pos = None

    for kind, data, pos in stream:
        if kind == TEXT:
            if tqueue_pos is not None:
                tqueue_data += data
            else:
                tqueue_pos = pos
                tqueue_data = data
        else:
            if tqueue_pos is not None:
                tqueue_data = tqueue_data.strip()
                if tqueue_data != "":
                    tqueue_data = wsre.sub(" ", tqueue_data)
                    yield TEXT, tqueue_data, tqueue_pos
                tqueue_pos = None
                tqueue_data = None
            yield kind, data, pos

    if tqueue_pos is not None:
        tqueue_data = tqueue_data.strip()
        if tqueue_data != "":
            tqueue_data = wsre.sub(" ", tqueue_data)
            yield TEXT, tqueue_data, tqueue_pos


def write_html(f, oscats, stds):
    loader = TemplateLoader(["web"])
    tmpl = loader.load("tbltmpl.xml")
    stream = tmpl.generate(oscats=oscats,
                           stds=stds,
                           enumerate=enumerate,
                           sorthdr=sorthdr,
                           cycle=itertools.cycle)
    for chunk in HTMLSerializer(doctype='html5')(collapse_ws_xml(stream)):
        f.write(chunk.encode('utf-8'))

def main():
    if len(sys.argv) == 1:
        dirname = "."
    elif (len(sys.argv) == 2
          and sys.argv[1] != "-h" and sys.argv[1] != "--help"):
        dirname = sys.argv[1]
    elif (len(sys.argv) == 3 and sys.argv[1] == "--"):
        dirname = sys.argv[2]
    else:
        sys.stderr.write("usage: " + os.basename(argv[0]) + " directory\n"
                         "Generates a table of header usage from h- and "
                         "b-files found in DIRECTORY.\n"
                         "Table is written to stdout.\n\n")
        if (len(sys.argv) == 2 and (sys.argv[1] == "-h" or
                                    sys.argv[1] == "--help")):
            sys.exit(0)
        else:
            sys.exit(2)

    rv, datasets = load_datasets(dirname)
    if rv != 0: sys.exit(rv)

    oscats, stds = preprocess(datasets)
    write_html(sys.stdout, oscats, stds)
    sys.exit(0)

if __name__ == '__main__': main()
