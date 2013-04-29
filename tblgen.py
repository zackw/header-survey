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
import copy
import errno
import itertools
import os
import re
import sys
import tempfile

import genshi
import genshi.builder
import genshi.input
import genshi.output
import genshi.template

from string import punctuation as _punctuation

# Generation number expected by the current revision of this program.
# Should match scansys.py.
INPUT_GENERATION_NO = 1

def sorthdr(hs):
    """Sort a list of pathnames, ASCII case-insensitively.
       All one-component pathnames are sorted ahead of all longer
       pathnames; within a group of multicomponent pathnames with the
       same leading component, all two-component pathnames are sorted
       ahead of all longer pathnames; and so on, recursively."""
    def hsortkey(h):
        def hsortkey_r(hd, *tl):
            if len(tl) == 0: return (0, hd)
            return (1, hd) + hsortkey_r(*tl)

        segs = h.lower().replace("\\", "/").split("/")
        return hsortkey_r(*segs)

    return sorted(hs, key=hsortkey)

# hat tip to http://code.activestate.com/recipes/285264-natural-string-sorting/
_natsort_split_re = re.compile(r'(\d+|\D+)')
def natsort_key(s):
    """Produce a sort key for 's' which causes runs of nondigits to be
       sorted ASCII case-insensitively, and runs of digits to be sorted
       numerically."""
    def try_int(s):
        try: return int(s)
        except: return s.lower()
    return tuple(try_int(c) for c in _natsort_split_re.findall(s))

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
    """Acts like a file, implements the Unix atomic update pattern:
       data is actually written to a temporary file in the same
       directory, then renamed over the original name on close.  In
       addition, if the new file's contents are identical to the old
       file, the old file is not modified."""
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

class HeaderNotes(object):
    """Data object representing what we know about one header on one
       OS.  The identity of the header and the OS are implicit.  It
       has a summary symbol, which is a set of letter codes, and a
       dictionary of annotations; annotations are keyed by a compiler
       label and each value is a list of strings."""

    _T = genshi.builder.tag

    def __init__(self, sym, cc1):
        self.sym = set(sym)
        self.cc1 = cc1
        self.ann = {}

    # Notes are not ordered, but can be equal or unequal.
    def __eq__(self, other):
        return self.sym == other.sym and self.ann == other.ann
    def __ne__(self, other):
        return self.sym != other.sym or  self.ann != other.ann

    def add_aline(self, line):
        if self.cc1 not in self.ann:
            self.ann[self.cc1] = []
        self.ann[self.cc1].append(line)

    def merge(self, h, other):
        """Merge OTHER's summary and annotations into this object."""
        self.sym |= other.sym
        for k, v in other.ann.items():
            if k in self.ann:
                if v == ['Absent.']:
                    assert self.ann[k] == ['Absent.']
                else:
                    self.ann[k].extend(v)
            else:
                self.ann[k] = v[:]
        if self.sym == set(('Y','N')):
            sys.stderr.write("YN: {}: {!r}\n".format(h, self.ann))

    def output_sym(self):
        """Generate HTML representing this object's symbol."""
        label = ''.join(c for c in ('Y', 'P', 'B', 'N')
                           if c in self.sym)
        if label == 'Y':
            if len(self.ann) != 0:
                raise RuntimeError("inconsistent notes: "
                                   "label={} sym={!r} ann={!r}"
                                   .format(label, self.sym, self.ann))
            elt = self._T.div
        elif label == 'N':
            for c, a in self.ann.iteritems():
                if a != ["Absent."]:
                    raise RuntimeError("inconsistent notes: "
                                       "label={} sym={!r} ann={!r}"
                                       .format(label, self.sym, self.ann))
            elt = self._T.div
        else:
            assert len(self.ann) > 0
            elt = self._T.summary

        return elt(label, class_ = label.lower())

    def output_ann(self):
        """Generate HTML representing this object's annotations."""
        _H = genshi.input.HTML
        _T = self._T

        assert len(self.ann) > 0
        merged_anns = {}
        final_anns = {}
        for k, v in self.ann.iteritems():
            v = " ".join(v)
            if v not in merged_anns: merged_anns[v] = []
            merged_anns[v].append(k)
        for k, v in merged_anns.iteritems():
            v.sort(key=natsort_key)
            final_anns[", ".join(v)] = k

        if len(final_anns) == 1:
            return _T.div(_H(final_anns.values()[0]))
        else:
            rv = _T.dl()
            for k in sorted(final_anns.iterkeys(), key=natsort_key):
                rv.append(_T.dt(k))
                rv.append(_T.dd(_H(final_anns[k])))
            return rv

    def output(self):
        """Generate HTML for this object."""
        sym = self.output_sym()
        if sym.tag != 'summary':
            return sym
        return self._T.details(sym, self.output_ann())

class Dataset(object):

    # These are the known metadata tags.  The default value also
    # controls the acceptable type.  A fully constructed instance
    # of this class will have all of these tags as attributes.
    tagdefaults = { "gen"      : 0,
                    "sequence" : 50,
                    "category" : "Uncategorized",
                    "compiler" : "Unknown",
                    "version"  : "Unknown",
                    "label"    : "Unknown",
                    }

    def __init__(self, items, tags):
        self.items = items

        # Set metadata from the tag dict. Ignore unrecognized tags.
        for tag, default in self.tagdefaults.iteritems():
            val = tags.get(tag)
            if val is not None:
                setattr(self, tag, type(default)(val))
            else:
                setattr(self, tag, default)

        self.absent = HeaderNotes('N', self.compiler)
        self.absent.add_aline("Absent.")

        # Set sort keys for specially sorted tags.
        # "embedded X" sorts immediately after X; otherwise,
        # categories are case-insensitive alphabetical
        if self.category.startswith("embedded "):
            self.catkey = (self.category[9:].lower(), 1)
        else:
            self.catkey = (self.category.lower(), 0)
        # numbers within label and version are sorted numerically
        self.labelkey = natsort_key(self.label)
        self.verskey = natsort_key(self.version)

    @classmethod
    def from_file(cls, fname):
        def file_label(fname):
            label = fname
            if fname.startswith("b-") or fname.startswith("h-"):
                label = label[2:]
            if fname.endswith(".txt"):
                label = label[:-4]
            label = label.replace("-", " ")

        tags = { 'label' : file_label(fname) }
        items = {}
        prev_item = None

        with open(fname, "rU") as fp:
            for lno, line in enumerate(fp):
                line = line.strip()
                if line == "" or line[0] == "#": continue
                if line[0] == ":":
                    prev_item = None
                    k, v = line[1:].split(None, 1)
                    d = cls.tagdefaults.get(k)
                    if d is not None:
                        tags[k] = type(d)(v)
                    # else: ignore unrecognized tags
                elif line[0] == '$':
                    l = line[1:].strip()
                    if prev_item is None:
                        raise RuntimeError("{}:{}: {!r}:"
                                           "annotation without header"
                                           .format(fname, lno+1, l))
                    prev_item.add_aline(l)
                else:
                    line = line.replace('\\', '/')
                    if line[0] in _punctuation:
                        p = line[0]
                        l = line[1:]
                        if p == '!': p = 'B'
                        elif p == '%': p = 'P'
                        else:
                            raise RuntimeError("{}:{}: "
                                               "unsupported tag symbol: {}"
                                               .format(fname, lno+1, p))
                    else:
                        p = 'Y'
                        l = line
                    if l in items:
                        raise RuntimeError("{}: duplicate header-line {!r}"
                                           .format(fname, line))
                    items[l] = prev_item = HeaderNotes(p, tags.get('compiler',
                                                                   ''))

        return cls(items, tags)

    def merge_compiler(self, other):
        assert self.label == other.label and self.version == other.version

        for (h, theirs) in other.items.iteritems():
            self.items[h].merge(h, theirs)

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

    def ensure(self, h):
        if h not in self.items:
            self.items[h] = copy.copy(self.absent)

def preprocess_osgrp(osgroup):
    assert len(frozenset(os.label for os in osgroup)) == 1

    versions = {}
    for os in osgroup:
        merged = versions.get(os.version, None)
        if merged is not None:
            merged.merge_compiler(os)
        else:
            versions[os.version] = os
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

    # expand all os-sets to include stub entries for all headers
    for og in osgrps.itervalues():
        for o in og:
            for s in stds:
                for h in s:
                    o.ensure(h)

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


# If someone can suggest a more elegant, or at least less repetitive,
# way to write this transform, I am all ears.
_wsre = re.compile(r'\s+', re.UNICODE)
def collapse_ws_xml(stream):
    wsre = _wsre
    tqueue_data = None
    tqueue_pos = None
    TEXT = genshi.core.TEXT

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
        self.oscats, self.stds = preprocess(datasets)
        self.tmpldir = args.template
        self.loader = genshi.template.TemplateLoader(self.tmpldir)

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
                               enumerate=enumerate,
                               sorthdr=sorthdr,
                               cycle=itertools.cycle)
        stream = collapse_ws_xml(stream)
        with UpdateIfChange(dstname) as f:
            for chunk in genshi.output.HTMLSerializer(doctype='html5')(stream):
                f.write(chunk.encode('utf-8'))

def main():
    argp = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
Generate a webpage showing per-OS availability of header files, from
the data files in DATADIR and the templates in TMPLDIR.  The page is
written to OUTDIR.
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
