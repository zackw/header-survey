#! /usr/bin/env python

# This script determines which subset of a large list of "common"
# header files (many are standard, some are not) are present on your
# operating system.  It does not attempt to distinguish between
# headers provided by the "core" operating system and headers provided
# by add-on packages, as this would require detailed understanding of
# the package management facilities.  If you wish, edit headers you
# know to be provided by optional packages out of the results.
#
# On the command line, specify the compiler to use and any additional
# arguments that may be necessary.  If no arguments are provided,
# defaults to "cc".
#
# The list of headers to look for is computed from the b- and r-files in
# the data/ directory.  You can override the location of this directory
# with the --datadir= command-line option, which must appear before the
# compiler and its options, if any.

import ConfigParser
import contextlib
import functools
import getopt
import itertools
import os
import platform
import shutil
import subprocess
import sys
import tempfile

# from http://code.activestate.com/recipes/578272-topological-sort/
def toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. Output is a list of
sets in topological order. The first set consists of items with no
dependences, each subsequent set consists of items that depend upon
items in the preceeding sets.

>>> print '\\n'.join(repr(sorted(x)) for x in toposort({
...     2: set([11]),
...     9: set([11,8]),
...     10: set([11,3]),
...     11: set([7,5]),
...     8: set([7,3]),
...     }) )
[3, 5, 7]
[8, 11]
[2, 9, 10]

"""

    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = \
        functools.reduce(set.union, data.itervalues()) - set(data.iterkeys())
    # Add empty dependences where needed
    for item in extra_items_in_deps:
      data[item] = set()
    while True:
        ordered = set(item for item, dep in data.iteritems() if not dep)
        if not ordered:
            break
        yield ordered
        ndata = {}
        for item, dep in data.iteritems():
           if item not in ordered:
               ndata[item] = dep - ordered
        data = ndata
    if len(data) > 0:
        raise RuntimeError("Cyclic dependencies exist among these items:\n"
                           + "\n".join(repr(x) for x in data.iteritems()))

# Topologically sort the common-headers list according to the prerequisites
# list, so that gensrc() can safely check whether probable-prerequisite
# headers are known to exist, and include them only if so.
def toposort_headers(headers, prerequisites):
    topo_in = {}
    for h in headers:
        topo_in[h] = set(prerequisites.get(h, []))
    return list(itertools.chain.from_iterable(toposort(topo_in)))

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

@contextlib.contextmanager
def fs_state():
    class fs_state_obj(object):
        def __init__(self, wd, devnull):
            self.wd = wd
            self.devnull = devnull
    wd = None
    devnull = None
    try:
        wd = tempfile.mkdtemp()
        devnull = open(os.devnull, "rb")
        yield fs_state_obj(wd, devnull)
    finally:
        if devnull is not None: devnull.close()
        if wd is not None: shutil.rmtree(wd)

def gensrc(state, header, known_headers, prerequisites, specials):
    def include(f, h):
        s = specials.get(h)
        if s is not None:
            f.write(s)
        else:
            for p in prerequisites.get(h, []):
                if p in known_headers:
                    include(f, p)
        f.write("#include <{0}>\n".format(os.path.join(*h.split("/"))))

    src = os.path.join(state.wd, "htest.c")
    with open(src, "w") as f:
        include(f, header)
        # End with a global definition, in case some compiler
        # doesn't like source files that define nothing.
        # The #undefs are probably unnecessary, but you never know.
        f.write("#undef int\n#undef main\n#undef void\n#undef return\n"
                "int main(void){return 0;}\n")
    return src

def invoke(state, argv):
    msg = os.path.join(state.wd, "htest-out.txt")
    with open(msg, "w") as stdo:
        stdo.write(" ".join(argv) + "\n")
        stdo.flush()
        try:
            rc = subprocess.call(argv,
                                 stdin=state.devnull,
                                 stdout=stdo,
                                 stderr=subprocess.STDOUT,
                                 cwd=state.wd)
            if rc != 0:
                stdo.write("exit {0}\n".format(rc))
        except EnvironmentError, e:
            if e.filename:
                label = e.filename
            else:
                label = argv[0]
            stdo.write("{0}: {1}\n".format(label, e.strerror))
            rc = -1
    return (rc, msg)

def probe_one(state, cc, debug, header, known_headers, prerequisites, specials):
    src = gensrc(state, header, known_headers, prerequisites, specials)
    (rc, msg) = invoke(state, cc + ["-c", src])
    if rc == 0:
        return True
    with open(msg, "rU") as f:
        errors = f.read().strip()

    if debug:
        sys.stderr.write("# {0} compilation failed:\n".format(header))
    else:
        (rc, msg) = invoke(state, cc + ["-E", src])
        if rc == 0:
            sys.stderr.write("# {0} present but cannot be compiled:\n"
                             .format(header))

    if rc == 0 or debug:
        for e in errors.split("\n"):
            sys.stderr.write("## {0}\n".format(e))
    if debug:
        sys.stderr.write("# failed program was:\n")
        for l in open(src, "rU").read().strip().split("\n"):
            sys.stderr.write("## {0}\n".format(l))

    return False

def probe(state, cc, debug, headers, prerequisites, specials):
    known_headers = set()
    for h in headers:
        if probe_one(state, cc, debug, h,
                     known_headers, prerequisites, specials):
            known_headers.add(h)
    return known_headers

def smoke(state, cc):
    # "Smoke test": If we cannot detect this header file, something is
    # so profoundly wrong that we shouldn't try to continue.
    src = gensrc(state, "stdarg.h", frozenset(), {}, {})
    (rc, msg) = invoke(state, cc + ["-c", src])
    if rc == 0:
        return
    with open(msg, "rU") as f:
        errors = f.read()
    sys.stderr.write("# stdarg.h not detected. Something is wrong "
                     "with your compiler:\n")
    for e in errors.split("\n"): sys.stderr.write("# {0}\n".format(e))
    sys.exit(1)

# Compute the set of headers to scan for -- that is, header files that
# you might reasonably expect to find on more than one system.  In the
# datadir, there are a bunch of "b-" files, which list headers defined
# by this or that standard; we simply take the union of all these lists.
def headers_to_probe(datadir):
    headers = set()
    basename = os.path.basename
    join = os.path.join
    for fn in os.listdir(datadir):
        tag = basename(fn)[:2]
        if tag == 'b-' and tag[-1] != '~':
            for l in open(join(datadir, fn), "rU"):
                l = l.strip()
                if l == "" or l[0] in ":#": continue
                headers.add(l)
    return headers

# Read prereqs.ini and generate the 'prerequisites' and 'specials'
# dictionaries.
def read_prereqs(fname):
    prerequisites = {}
    specials = {}
    parser = ConfigParser.ConfigParser()
    parser.read(fname)

    if parser.has_section("prerequisites"):
        for h in parser.options("prerequisites"):
            prerequisites[h] = parser.get("prerequisites", h).split()
    if parser.has_section("special"):
        for h in parser.options("special"):
            specials[h] = parser.get("special", h).strip() + "\n"

    return prerequisites, specials

class Args(object):
    def usage(self, argv0, errmsg=""):
        argv0 = os.path.basename(argv0)
        if errmsg != "":
            exitcode = 2
            f = sys.stderr
            f.write("%s: %s\n" % (argv0, errmsg))
        else:
            exitcode = 0
            f = sys.stdout

        f.write("Usage: %s [OPTIONS] [COMPILER AND ARGS]\n"
                "Probe COMPILER for set of supported common header files.\n"
                "COMPILER defaults to 'cc'.  List is written to stdout.\n\n"
                "Options:\n"
                "  -h, --help            display command line help\n"
                "  --debug               report all compiler errors\n"
                "  --datadir=DIRECTORY   directory containing lists of header"
                                         "files to probe\n"
                "  --prereqs=FILE        file listing prerequisite sets for"
                                         "each header\n"
                % argv0)
        sys.exit(exitcode)

    def __init__(self, argv):
        # defaults
        self.cc = ["cc"]
        self.debug = False
        self.datadir = "data"
        self.prereqs = "prereqs.ini"

        try:
            opts, args = getopt.getopt(argv[1:], "h",
                                       ["help", "debug",
                                        "datadir=", "prereqs="])
        except getopt.GetoptError, e:
            self.usage(argv[0], str(e))

        for o, a in opts:
            if o == "--datadir":
                self.datadir = a
            elif o == "--prereqs":
                self.prereqs = a
            elif o == "--debug":
                self.debug = True
            elif o in ("-h", "--help"):
                self.usage(argv[0])
            else:
                self.usage(argv[0], "impossible argument %s %s" % (o, a))

        if len(args) > 0:
            self.cc = args

def main(argv, stdout, stderr):
    args = Args(argv)
    try:
        with fs_state() as state:
            smoke(state, args.cc)
            prerequisites, specials = read_prereqs(args.prereqs)
            headers = toposort_headers(headers_to_probe(args.datadir),
                                       prerequisites)
            avail_headers = probe(state, args.cc, args.debug,
                                  headers, prerequisites, specials)
        stdout.write("# build platform: " + platform.platform() + "\n")
        if len(args.cc) > 1:
            stdout.write("# compiler: " + " ".join(args.cc) + "\n")
        stdout.write(":category unknown\n:label unknown\n")
        for h in sorthdr(avail_headers):
            stdout.write(h + "\n")
        return 0
    except EnvironmentError, e:
        stderr.write("%s: %s\n" % (e.filename, e.strerror))
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv, sys.stdout, sys.stderr))
