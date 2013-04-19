#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright 2013 Zack Weinberg <zackw@panix.com> and other contributors.
#
# Copying and distribution of this program, with or without
# modification, is permitted in any medium without royalty provided
# the copyright notice and this notice are preserved.  It is offered
# as-is, without any warranty.

# Note to contributors: Unlike scansys.py, this program only needs to
# work with Python 2.7.  Some code is functionally duplicated from
# scansys.py but with the compatibility contortions removed; this is
# why there is no shared support library.
#
# It requires the Genshi template library, and is likely to grow
# dependencies on other third-party libraries in the future (such as
# CSS and JS minifiers).

from __future__ import unicode_literals

import argparse
import ConfigParser
import errno
import itertools
import os
import re
import sys
import tempfile

from genshi.core import TEXT
from genshi.builder import tag as Tag
from genshi.input import HTML
from genshi.output import HTMLSerializer
from genshi.template import TemplateLoader
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

make_id_re=re.compile(r'[^A-Za-z0-9_]')
def make_id(s):
    s = make_id_re.sub("_", s)
    if s[0] in "0123456789": s = "_"+s
    return s

# hat tip to http://code.activestate.com/recipes/285264-natural-string-sorting/
_natsort_split_re = re.compile(r'(\d+|\D+)')
def natsort_key(s):
    def try_int(s):
        try: return int(s)
        except: return s.lower()
    return tuple(try_int(c) for c in _natsort_split_re.findall(s))

# http://code.activestate.com/recipes/511480-interleaving-sequences/
def interleave(*args):
    for idx in range(0, max(len(arg) for arg in args)):
        for arg in args:
            try:
                yield arg[idx]
            except IndexError:
                continue

# Create/update files only if necessary.
# This may not be as thorough as it needs to be.
def ensure_all_directories(path):
    """Make sure that all components of PATH exist and are
       directories.  No-op if they already do.  PATH should be
       normalized (e.g. via os.path.normpath or os.path.realpath)."""
    try:
        os.makedirs(path)
    except EnvironmentError, e:
        if e.errno != errno.EEXIST:
            raise

class UpdateIfChange(file):
    def __init__(self, fname, binary=False):
        self.path = os.path.realpath(fname)
        dname = os.path.dirname(self.path)
        ensure_all_directories(dname)
        (fd, tmppath) = tempfile.mkstemp(dir=dname)
        self.tmppath = tmppath
        # the file constructor takes only a name, so we have to reopen
        # we hang onto the original fd for use later
        self.fd = fd
        file.__init__(self, tmppath, 'w' + ('b' if binary else ''))

    def close(self):
        file.close(self)
        nfd = self.fd
        ofd = None
        try:
            # Compare the old and new files.  If they are identical,
            # just delete the new file.  If the old file doesn't exist,
            # create it now; this streamlines processing below, at the
            # cost of a little additional inode churn.
            ofd = os.open(self.path, os.O_RDWR | os.O_CREAT)
            ost = os.fstat(ofd)
            nst = os.fstat(nfd)

            if ost.st_nlink != 1:
                os.close(ofd)
                os.close(nfd)
                raise RuntimeError("cannot atomically update {!r} with {} links"
                                   .format(self.path, ost.st_nlink))

            # If they're not the same size they cannot be identical.
            if ost.st_size == nst.st_size:
                os.lseek(ofd, 0, os.SEEK_SET)
                if os.read(nfd, ost.st_size) == os.read(ofd, ost.st_size):
                    # Identical.
                    os.close(ofd)
                    os.close(nfd)
                    os.unlink(self.tmppath)
                    return

            # Not identical, so we need to update.  Copy permissions
            # from ofd to nfd, then rename tmppath over path.
            # Assumes Unixy rename() semantics.  Does not copy ACLs
            # or extended attributes (if there's an existing library
            # to deal with that, please let me know about it).
            # Only do fchown() if it would make a difference, since
            # we may not have the privilege to use it.
            if ost.st_uid != nst.st_uid or ost.st_gid != nst.st_gid:
                os.fchown(nfd, ost.st_uid, ost.st_gid)
            os.fchmod(nfd, ost.st_mode)
            os.close(ofd)
            os.fsync(nfd)
            os.close(nfd)
            os.rename(self.tmppath, self.path)
            return

        # Make sure to clean up if any of the above processing raises
        # an exception.  This is not a finally: because we don't want
        # to do it if nothing went wrong.
        except:
            if ofd is not None: os.close(ofd)
            os.close(nfd)
            os.unlink(self.tmppath)
            raise

def update_directory_tree(srcdir, dstdir, process_file):
    """Update the contents of DSTDIR based on the contents of SRCDIR.
       For each file below SRCDIR, process_file will be called with
       arguments (srcpath, dstpath, fname) where srcpath/fname is the
       file and dstpath is the subdirectory of DSTDIR corresponding to
       srcpath.  dstpath is not guaranteed to exist when process_file
       is called.  process_file should return a list of all the
       pathnames it has created or updated in response to this call;
       these pathnames should all start with 'dstpath'.  Once SRCDIR
       has been completely walked, DSTDIR is walked depth-first and
       all files that were not reported by process_file are deleted,
       plus all empty directories (except DSTDIR itself)"""
    pjoin   = os.path.join
    relpath = os.path.relpath
    normpath = os.path.normpath
    dirname = os.path.dirname
    keep_files = set()
    keep_dirs = set()
    success = True
    def report_error(exc):
        sys.stderr.write("{}: {}\n".format(exc.filename, exc.strerror))
        success = False

    for (srcpath, dirs, files) in os.walk(srcdir, onerror=report_error):
        dstpath = normpath(pjoin(dstdir, relpath(srcpath, srcdir)))
        for f in files:
            for created in process_file(srcpath, dstpath, f):
                if not created.startswith(dstpath):
                    raise RuntimeError("{} not within {}"
                                       .format(created, dstpath))
                keep_files.add(created)
                keep_dirs.add(dirname(created))
    if not success:
        raise SystemExit(1)

    for (path, dirs, files) in os.walk(dstdir, onerror=report_error,
                                       topdown=False):
        for f in files:
            p = pjoin(path, f)
            if p not in keep_files:
                try: os.unlink(p)
                except EnvironmentError, e: report_error(e)
        for d in dirs:
            p = pjoin(path, d)
            if p not in keep_dirs:
                try: os.rmdir(p)
                except EnvironmentError, e: report_error(e)
    if not success:
        raise SystemExit(1)


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
            list.__init__(self)
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

def load_datasets(dirname):
    datasets = []
    rv = 0
    try:
        files = os.listdir(dirname)
    except EnvironmentError, e:
        sys.stderr.write("{}: {}\n".format(e.filename, e.strerror))
        raise SystemExit(1)

    for fname in files:
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

    if rv != 0: raise SystemExit(rv)
    return datasets

def load_prereqs(fname):
    """Read prereqs.ini and generate a table of each header's prerequisites.
       The return value is a dictionary mapping each header in the .ini to
       an *expanded* (transitive) list of its prerequisites.
       For specials, the dictionary entry is instead the text of the
       first comment in the special declaration."""

    ecre = re.compile(r'(?s)/\* *(.*?) *\*/')
    def extract_comment(text):
        m = ecre.search(text)
        if not m: return "???special without explanation???"
        return HTML(m.group(1).decode('utf-8'))

    def expand_prereq(h, prereqs):
        r = set()
        for p in prereqs.get(h, []):
            r.add(p)
            r |= expand_prereq(p, prereqs)
        return r

    def prereq_note(prereqs):
        pq = sorthdr(prereqs)
        if len(pq) == 1:
            return Tag("May require ", Tag.code(pq[0]), ".")
        elif len(pq) == 2:
            return Tag("May require ", Tag.code(pq[0]),
                       " and/or ", Tag.code(pq[1]), ".")
        else:
            l = [Tag.code(p) for p in pq]
            s = (", ",)*(len(l) - 2) + (", and ",)
            r = tuple(interleave(l, s))
            return Tag(*(("May require some or all of: ",) + r + (".",)))

    prerequisites = {}
    specials = {}
    parser = ConfigParser.ConfigParser()
    parser.read(fname)

    if parser.has_section("prerequisites"):
        for h in parser.options("prerequisites"):
            prerequisites[h.strip()] = \
                parser.get("prerequisites", h).split()
    if parser.has_section("special"):
        for h in parser.options("special"):
            specials[h] = parser.get("special", h).strip()

    expanded = {}
    for h in prerequisites:
        expanded[h] = [prereq_note(expand_prereq(h, prerequisites))]
    for h in specials:
        assert h not in expanded
        expanded[h] = [extract_comment(specials[h])]

    return expanded


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
                tqueue_data = wsre.sub(" ", tqueue_data)
                if tqueue_data != "" and tqueue_data != " ":
                    yield TEXT, tqueue_data, tqueue_pos
                tqueue_pos = None
                tqueue_data = None
            yield kind, data, pos

    if tqueue_pos is not None:
        tqueue_data = tqueue_data.strip()
        if tqueue_data != "":
            tqueue_data = wsre.sub(" ", tqueue_data)
            yield TEXT, tqueue_data, tqueue_pos

class PageWriter(object):
    def __init__(self, args):
        datasets = load_datasets(args.datadir)
        self.notes = load_prereqs(args.prereqs)
        self.oscats, self.stds = preprocess(datasets)
        self.tmpldir = args.template
        self.loader = TemplateLoader(self.tmpldir)

    def __call__(self, srcdir, dstdir, fname):
        # ignore editor backup files
        if fname[-1] == '~' or (fname[0] == '#' and fname[-1] == '#'):
            return []

        srcname = os.path.join(srcdir, fname)
        (base, ext) = os.path.splitext(fname)
        dstname = os.path.join(dstdir, base)

        if ext == '.tmpl':
            dstname += '.html'
            self.write_tmpl(srcname, dstname)
        else:
            dstname += ext
            self.copy_file(srcname, dstname)

        return [dstname]

    def copy_file(self, srcname, dstname):
        with UpdateIfChange(dstname, binary=True) as to:
            with open(srcname, 'rb') as frm:
                to.write(frm.read())

    def write_tmpl(self, srcname, dstname):
        tmpl = self.loader.load(os.path.relpath(srcname, self.tmpldir))
        stream = tmpl.generate(oscats=self.oscats,
                               stds=self.stds,
                               notes=self.notes,
                               enumerate=enumerate,
                               sorthdr=sorthdr,
                               make_id=make_id,
                               cycle=itertools.cycle)
        stream = collapse_ws_xml(stream)
        with UpdateIfChange(dstname) as f:
            for chunk in HTMLSerializer(doctype='html5')(stream):
                f.write(chunk.encode('utf-8'))

def main():
    argp = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
Generate a webpage showing per-OS availability of header files, from
the data files in DATADIR, the prerequisite table PREREQS, and the
templates in TMPLDIR.  The page is written to OUTDIR.
""")
    # Monkey-patch out the stupid hardwired names for arguments and options.
    # There doesn't appear to be any better way to do this (stuffing
    # everything in a group of our own works but then we have to implement
    # --help by hand).
    for g in getattr(argp, '_action_groups', []):
        if g.title == 'positional arguments':
            g.title = 'arguments'
        elif g.title == 'optional arguments':
            g.title = 'options'

    argp.add_argument('-d', '--datadir', metavar='DATADIR',
                      help='directory containing lists of header files per OS',
                      default='data')
    argp.add_argument('-p', '--prereqs', metavar='PREREQS',
                      help='file listing prerequisite sets for each header',
                      default='prereqs.ini')
    argp.add_argument('-t', '--template', metavar='TMPLDIR',
                      help='directory containing template for webpage',
                      default='tmpl')
    argp.add_argument('-o', '--output', metavar='OUTDIR',
                      help='output directory; contents will be overwritten!',
                      default='web')

    args = argp.parse_args()
    writer = PageWriter(args)
    update_directory_tree(args.template, args.output, writer)

if __name__ == '__main__': main()
