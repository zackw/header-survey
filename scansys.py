#! /usr/bin/env python
# Copyright 2013 Zack Weinberg <zackw@panix.com> and other contributors.
#
# Copying and distribution of this program, with or without
# modification, is permitted in any medium without royalty provided
# the copyright notice and this notice are preserved.  It is offered
# as-is, without any warranty.

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
# defaults to "cc".  You can also control this script's behavior to
# some extent with command-line options, which must appear before the
# compiler to use, so they aren't confused with arguments to the
# compiler.
#
# The list of headers to look for is taken from the union of all
# b- files in the "data/" directory.  You can override the location of
# this directory with --datadir.  There is also a configuration file
# which defines "prerequisites" -- headers which cannot just be
# included in isolation.  This defaults to "prereqs.ini", which can be
# overridden with --prereqs.  Finally, if results are not as expected,
# --debug will cause the script to print extra information about
# failed probes on stderr.

# This script is backward compatible all the way to Python 2.0, and
# therefore uses many constructs which are considered obsolete, and
# avoids many conveniences added after that point.

import ConfigParser
import StringIO
import getopt
import os
import re
import shutil
import sys

# see if we have sets; if not, provide a replacement that does enough
try:
    Set = set
except NameError:
    try:
        from sets import Set
    except ImportError:
        class Set:
            def __init__(self, *items):
                self.items = {}
                for x in items:
                    for xx in x:
                        self.items[xx] = 1
            def __len__(self):
                return len(self.items)
            def __contains__(self, x):
                return self.items.get(x) is not None
            def __iter__(self):
                return self.items.keys()
            # for pre-__iter__ interpreters
            def __getitem__(self, n):
                return self.items.keys()[n]
            def add(self, x):
                self.items[x] = 1
            def discard(self, x):
                try: del self.items[x]
                except KeyError: pass
            def copy(self):
                return Set(self.items.keys())
            def update(self, other):
                for x in other:
                    self.items[x] = 1
            def union(self, other):
                new = self.copy()
                new.update(other)
                return new
            __and__ = union
            def difference_update(self, other):
                for x in other:
                    self.discard(x)
            def difference(self, other):
                new = self.copy()
                new.difference_update(other)
                return new
            __sub__ = difference

# It may be necessary to monkey-patch ConfigParser to accept / in an
# option name.
def maybe_fix_ConfigParser():
    p = ConfigParser.ConfigParser()
    test = StringIO.StringIO("[x]\na/b=c/d\n")
    try:
        p.readfp(test)
    except ConfigParser.ParsingError:
        if not getattr(ConfigParser.ConfigParser, 'OPTCRE'):
            raise # we don't know what to do
        ConfigParser.ConfigParser.OPTCRE = re.compile(
            # this is a modified definition from 2.7
            r'(?P<option>[^:=\s]+)'      # very permissive!
            r'\s*(?P<vi>[:=])\s*'        # any number of space/tab,
                                         # followed by separator
                                         # (either : or =), followed
                                         # by any # space/tab
            r'(?P<value>.*)$'            # everything up to eol
            )
        p = ConfigParser.ConfigParser()
        p.readfp(test)

maybe_fix_ConfigParser()

# provide mkdtemp if necessary
try:
    from tempfile import mkdtemp
except ImportError:
    import errno
    def mkdtemp():
        for i in xrange(os.TMP_MAX):
            name = os.tmpnam()
            try:
                os.mkdir(name, 0700)
                return name
            except OSError, e:
                if e.errno == errno.EEXIST:
                    continue
                raise
        raise OSError, (errno.EEXIST,
                        "No usable temporary directory name found")

# platform identification
def platform_id():
    try:
        import platform
        return platform.platform()
    except ImportError:
        try:
            return " ".join(os.uname())
        except AttributeError:
            return sys.platform

# opening a file in "rU" mode on a Python that doesn't support it
# ... silently succeeds!  So we can't use it at all.  Regex time!
def universal_readlines(fname):
    f = open(fname, "rb")
    s = f.read().strip()
    return re.split("\r|\n|\r\n", s)

# We can't use subprocess, it's too new.  We can't use os.popen*,
# because they don't report the exit code.  So... os.system it is.
# Which means we have to shell-quote, and shell-quoting for Windows
# is different than shell-quoting for Unix; the library *may* have
# the right stuff, somewhere, or then again it may not.
if sys.platform == "win32":
    try:
        from subprocess import list2cmdline
    except:
        def list2cmdline(seq):
            # See
            # http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
            # or search http://msdn.microsoft.com for
            # "Parsing C++ Command-Line Arguments"
            result = []
            needquote = 0
            for arg in seq:
                bs_buf = []

                # Add a space to separate this argument from the others
                if result:
                    result.append(' ')

                needquote = (" " in arg) or ("\t" in arg) or not arg
                if needquote:
                    result.append('"')

                for c in arg:
                    if c == '\\':
                        # Don't know if we need to double yet.
                        bs_buf.append(c)
                    elif c == '"':
                        # Double backslashes.
                        result.append('\\' * len(bs_buf)*2)
                        bs_buf = []
                        result.append('\\"')
                    else:
                        # Normal char
                        if bs_buf:
                            result.extend(bs_buf)
                            bs_buf = []
                        result.append(c)

                # Add remaining backslashes, if any.
                if bs_buf:
                    result.extend(bs_buf)

                if needquote:
                    result.extend(bs_buf)
                    result.append('"')

            return ''.join(result)
else:
    try:
        import shlex
        shellquote1 = shlex.quote
    except:
        import pipes
        shellquote1 = pipes.quote
    def list2cmdline(seq):
        return " ".join([shellquote1(s) for s in seq])

# from http://code.activestate.com/recipes/578272-topological-sort/
def toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. Output is a list of
sets in topological order. The first set consists of items with no
dependences, each subsequent set consists of items that depend upon
items in the preceeding sets.

>>> print '\\n'.join(repr(sorted(x)) for x in toposort({
...     2: Set([11]),
...     9: Set([11,8]),
...     10: Set([11,3]),
...     11: Set([7,5]),
...     8: Set([7,3]),
...     }) )
[3, 5, 7]
[8, 11]
[2, 9, 10]

"""

    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = Set()
    for s in data.values():
        extra_items_in_deps.update(s)
    extra_items_in_deps.difference_update(data.keys())
    # Add empty dependences where needed
    for item in extra_items_in_deps:
        data[item] = Set()

    result = []
    while 1:
        ordered = Set()
        for item, dep in data.items():
            if not dep:
                ordered.add(item)
        if not ordered:
            break
        result.append(ordered)
        ndata = {}
        for item, dep in data.items():
           if item not in ordered:
               ndata[item] = dep - ordered
        data = ndata
    if len(data) > 0:
        raise RuntimeError("Cyclic dependencies exist among these items:\n"
                           + "\n".join([repr(x) for x in data.items()]))
    return result

# Topologically sort the common-headers list according to the prerequisites
# list, so that gensrc() can safely check whether probable-prerequisite
# headers are known to exist, and include them only if so.
def toposort_headers(headers, prerequisites):
    topo_in = {}
    for h in headers:
        topo_in[h] = Set(prerequisites.get(h, []))
    topo_out = toposort(topo_in)
    rv = []
    for l in topo_out: rv.extend(l)
    return rv

# Sort a list of pathnames, ASCII case-insensitively.  All
# one-component pathnames are sorted ahead of all longer pathnames;
# within a group of multicomponent pathnames with the same leading
# component, all two-component pathnames are sorted ahead of all
# longer pathnames; and so on, recursively.

def hsortkey_r(hd, *tl):
    if len(tl) == 0: return (0, hd)
    return (1, hd) + hsortkey_r(*tl)

def hsortkey(h):
    segs = h.lower().replace("\\", "/").split("/")
    return hsortkey_r(*segs)

def sorthdr(hs):
    try:
        return sorted(hs, key=hsortkey)
    except NameError:
        # key= and sorted() were both added in 2.4
        # implement the Schwartzian Transform by hand
        khs = [(hsortkey(h), h) for h in hs]
        khs.sort()
        return [x[1] for x in khs]

# Filesystem state.
class ScratchDir:
    def __init__(self):
        # grab these in case __del__ gets called at a bad time
        self.rmtree = shutil.rmtree
        self.cd = os.chdir

        self.oldwd = os.getcwd()
        self.wd = mkdtemp()
        self.cd(self.wd)

    def close(self):
        # This is exceedingly paranoid since we want it to work
        # regardless of how constructed the object got.
        rmtree = getattr(self, 'rmtree', None)
        cd = getattr(self, 'cd', None)
        oldwd = getattr(self, 'oldwd', None)
        wd = getattr(self, 'wd', None)
        if (rmtree is not None and cd is not None and
            oldwd is not None and wd is not None):
            cd(oldwd)
            rmtree(wd)
        self.wd = None

    __del__ = close

def include(f, h, prerequisites, specials, known_headers):
    s = specials.get(h)
    if s is not None:
        f.write(s)
    else:
        for p in prerequisites.get(h, []):
            if p in known_headers:
                include(f, p, prerequisites, specials, known_headers)
    f.write("#include <%s>\n" % (os.path.join(*h.split("/"))))

def gensrc(scratch, header, known_headers, prerequisites, specials):
    src = os.path.join(scratch.wd, "htest.c")
    f = open(src, "w")
    include(f, header, prerequisites, specials, known_headers)
    # End with a global definition, in case some compiler
    # doesn't like source files that define nothing.
    # The #undefs are probably unnecessary, but you never know.
    f.write("#undef int\n#undef main\n#undef void\n#undef return\n"
            "int main(void){return 0;}\n")
    f.close()
    return src

def invoke(scratch, argv):
    # for a wonder, the incantation to redirect both stdout and
    # stderr to a file is exactly the same on Windows as on Unix!
    cmdline = list2cmdline(argv) + " > htest-out.txt 2>&1"
    msg = [cmdline]
    try:
        rc = os.system(cmdline)
        msg.extend(universal_readlines("htest-out.txt"))
    except EnvironmentError, e:
        if e.filename:
            msg.append("%s: %s" % (e.filename, e.strerror))
        else:
            msg.append("%s: %s" % (argv[0], e.strerror))
    return (rc, msg)

def probe_one(scratch, cc, debug, header, known_headers, prerequisites, specials):
    src = gensrc(scratch, header, known_headers, prerequisites, specials)
    (rc, errors) = invoke(scratch, cc + ["-c", src])
    if rc == 0:
        return 1

    if debug:
        sys.stderr.write("# %s compilation failed:\n" % header)
    else:
        (rc, errors) = invoke(scratch, cc + ["-E", src])
        if rc == 0:
            sys.stderr.write("# %s present but cannot be compiled:\n"
                             % header)

    if rc == 0 or debug:
        for e in errors:
            sys.stderr.write("## %s\n" % e)
    if debug:
        sys.stderr.write("# failed program was:\n")
        for l in universal_readlines(src):
            sys.stderr.write("## %s\n" % l)

    return 0

def probe(scratch, cc, debug, headers, prerequisites, specials):
    known_headers = Set()
    for h in headers:
        if probe_one(scratch, cc, debug, h,
                     known_headers, prerequisites, specials):
            known_headers.add(h)
    return known_headers

def smoke(scratch, cc):
    # "Smoke test": If we cannot detect this header file, something is
    # so profoundly wrong that we shouldn't try to continue.
    src = gensrc(scratch, "stdarg.h", Set(), {}, {})
    (rc, errors) = invoke(scratch, cc + ["-c", src])
    if rc == 0:
        return
    sys.stderr.write("# stdarg.h not detected. Something is wrong "
                     "with your compiler:\n")
    for e in errors:
        sys.stderr.write("# %s\n" % e)
    sys.exit(1)

# Compute the set of headers to scan for -- that is, header files that
# you might reasonably expect to find on more than one system.  In the
# datadir, there are a bunch of "b-" files, which list headers defined
# by this or that standard; we simply take the union of all these lists.
def headers_to_probe(datadir):
    headers = Set()
    basename = os.path.basename
    join = os.path.join
    for fn in os.listdir(datadir):
        tag = basename(fn)[:2]
        if tag == 'b-' and tag[-1] != '~':
            for l in universal_readlines(join(datadir, fn)):
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
            prerequisites[h.strip()] = parser.get("prerequisites", h).split()
    if parser.has_section("special"):
        for h in parser.options("special"):
            specials[h] = parser.get("special", h).strip() + "\n"

    return prerequisites, specials

class Args:
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
        self.debug = 0
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
                self.debug = 1
            elif o in ("-h", "--help"):
                self.usage(argv[0])
            else:
                self.usage(argv[0], "impossible argument %s %s" % (o, a))

        if len(args) > 0:
            self.cc = args

def main(argv, stdout, stderr):
    args = Args(argv)
    scratch = None
    prerequisites, specials = read_prereqs(args.prereqs)
    headers = toposort_headers(headers_to_probe(args.datadir),
                               prerequisites)
    try:
        scratch = ScratchDir()
        smoke(scratch, args.cc)
        avail_headers = probe(scratch, args.cc, args.debug,
                              headers, prerequisites, specials)
        scratch.close()

        stdout.write("# host OS: " + platform_id() + "\n")
        if len(args.cc) > 1:
            stdout.write("# compiler: " + " ".join(args.cc) + "\n")
        stdout.write(":category unknown\n:label unknown\n")
        for h in sorthdr(avail_headers):
            stdout.write(h + "\n")
        return 0
    except EnvironmentError, e:
        scratch.close()
        stderr.write("%s: %s\n" % (e.filename, e.strerror))
        return 1
    except:
        scratch.close()
        raise

if __name__ == '__main__':
    sys.exit(main(sys.argv, sys.stdout, sys.stderr))
