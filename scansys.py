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
# defaults to "cc".  WARNING: because we can't reliably predict all of
# the files that will be created during the probe process, the script
# changes into a temporary directory.  Therefore, if the compiler to
# use isn't in $PATH, it must be named by absolute pathname, and any
# pathnames in the compiler's arguments must also be absolute.
#
# You can also control this script's behavior to some extent with
# command-line options, which must appear before the compiler to use,
# so they aren't confused with arguments to the compiler. The list of
# headers to look for is taken from the union of all b- files in the
# "data/" directory.  You can override the location of this directory
# with --datadir.  There is also a configuration file which defines
# "prerequisites" -- headers which cannot just be included in
# isolation.  This defaults to "prereqs.ini", which can be overridden
# with --prereqs.  Finally, if results are not as expected, --debug
# will cause the script to print extra information about failed probes
# on stderr.

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

# suppress all Python warnings, since we deliberately use deprecated
# things (that were the only option in 2.0)
try:
    import warnings
    warnings.simplefilter("ignore")
except:
    pass

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

# opening a file in "rU" mode on a Python that doesn't support it
# ... silently succeeds!  So we can't use it at all.  Regex time!
_universal_readlines_re = re.compile("\r|\n|\r\n")
def universal_readlines(fname):
    f = open(fname, "rb")
    s = f.read().strip()
    if s == "": return []
    return _universal_readlines_re.split(s)

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
        # shlex.quote is the documented API for Bourne-shell
        # quotation, but was only added very recently.  Note that it
        # only does one argument.
        import shlex
        shellquote1 = shlex.quote
    except:
        # pipes.quote is undocumented but has existed all the way back
        # to 2.0.  It is semantically identical to shlex.quote.
        import pipes
        shellquote1 = pipes.quote
    def list2cmdline(seq):
        return " ".join([shellquote1(s) for s in seq])

def invoke(argv):
    """Invoke the command in 'argv' and capture its output."""
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

# platform identification
def platform_id():
    try:
        import platform
        x = platform.uname()
        return platform.system_alias(x[0], x[2], x[3])
    except ImportError:
        try:
            x = os.uname()
            return (x[0], x[2], x[3])
        except AttributeError:
            return (sys.platform, "unknown", "unknown")

_compiler_id_stop_re = re.compile(
    r'unrecognized option|must have argument|not found|warning|error|usage|'
    r'must have argument|copyright|informational note 404|no input files',
                  re.IGNORECASE)

def _compiler_id_1(cc, opt):
    # some versions of HP cc won't print their version info unless you
    # give them something to compile, le sigh
    made_dummy_i = 0
    if opt.endswith("dummy.i"):
        made_dummy_i = 1
        open("dummy.i", "w").write("int foo;\n")
    (stdin, stdout) = os.popen4(cc + " " + opt)
    stdin.close()

    results = []

    for l in stdout.read().split("\n"):
        l = l.strip()
        if l == "": continue
        if _compiler_id_stop_re.search(l): break
        results.append(l)

    stdout.close()
    return results

def compiler_id(cc):
    # gcc, clang: --version
    # sun cc, compaq cc, HP CC: -V
    # mipspro cc: -version
    # xlc: -qversion
    # -qversion is first because xlc's behavior upon receiving an unrecognized
    # option is to dump out its _entire manpage!_
    for opt in ("-qversion", "--version", "-V", "-version", "-V -c dummy.i"):
        r = _compiler_id_1(cc, opt)
        if len(r) > 0:
            return r
    return []

# from http://code.activestate.com/recipes/578272-topological-sort/
def toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
and whose values are lists of dependent items. Output is a list of
lists in topological order. The first list consists of items with no
dependences, each subsequent list consists of items that depend upon
items in the preceding list.  Order within lists is not meaningful.

>>> print '\\n'.join(repr(sorted(x)) for x in toposort({
...     2: [11],
...     9: [11,8],
...     10: [11,3],
...     11: [7,5],
...     8: [7,3],
...     }) )
[3, 5, 7]
[8, 11]
[2, 9, 10]

"""
    # Convert input lists to dictionaries.
    # Ignore self-dependencies.
    ndata = {}
    for k, v in data.items():
        nv = {}
        for d in v:
            if d != k:
                nv[d] = 1
        ndata[k] = nv
    data = ndata

    # Find all items that don't depend on anything.
    # Add empty dependences where needed.
    extra_items_in_deps = {}
    for s in data.values():
        extra_items_in_deps.update(s)
    for item in extra_items_in_deps.keys():
        if data.get(item, None) is None:
            data[item] = {}

    result = []
    while 1:
        ordered = {}
        for item, dep in data.items():
            if not dep:
                ordered[item] = 1
        if not ordered:
            break
        result.append(ordered.keys())
        ndata = {}
        for item, dep in data.items():
           if ordered.get(item, None) is None:
               for o in ordered.keys():
                   try: del dep[o]
                   except KeyError: pass
               ndata[item] = dep
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
        topo_in[h] = prerequisites.get(h, [])
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

class HeaderProber:
    """Engine class - this does all the real work."""

    def __init__(self, args):
        self.debug = args.debug
        self.cc = args.cc
        self.read_prereqs(args.prereqs)
        self.read_headers(args.datadir)

    def read_prereqs(self, prereqs):
        """Read prereqs.ini and generate the 'prerequisites' and 'specials'
           dictionaries."""
        prerequisites = {}
        specials = {}
        parser = ConfigParser.ConfigParser()
        parser.read(prereqs)

        if parser.has_section("prerequisites"):
            for h in parser.options("prerequisites"):
                prerequisites[h.strip()] = \
                    parser.get("prerequisites", h).split()
        if parser.has_section("special"):
            for h in parser.options("special"):
                specials[h] = parser.get("special", h).strip() + "\n"

        self.prerequisites = prerequisites
        self.specials = specials

    def read_headers(self, datadir):
        """Compute the set of headers to scan for -- that is, header
           files that you might reasonably expect to find on more than
           one system.  In the datadir, there are a bunch of "b-"
           files, which list headers defined by this or that standard;
           we simply take the union of all these lists."""
        headers = {}
        basename = os.path.basename
        join = os.path.join
        for fn in os.listdir(datadir):
            tag = basename(fn)[:2]
            if tag == 'b-' and tag[-1] != '~':
                for l in universal_readlines(join(datadir, fn)):
                    l = l.strip()
                    if l == "" or l[0] in ":#": continue
                    headers[l] = 1

        self.headers = toposort_headers(headers.keys(), self.prerequisites)

    def include(self, f, h):
        """Subroutine of gensrc, handles one header."""
        s = self.specials.get(h)
        if s is not None:
            f.write(s)
        else:
            for p in self.prerequisites.get(h, []):
                # only include this prereq if it's available and not buggy
                state = self.known_headers.get(p, None)
                if type(state) == type(""):
                    self.include(f, p)
                elif self.debug:
                    sys.stderr.write("%s: skipping prereq %s: state=%s\n"
                                     % (h, p, repr(state)))
        f.write("#include <%s>\n" % (os.path.join(*h.split("/"))))

    def gensrc(self, header, bare):
        """Generate a source file that tests the inclusion of HEADER."""
        src = "htest.c"
        f = open(src, "w")
        if bare:
            f.write("#include <%s>\n" % (os.path.join(*header.split("/"))))
        else:
            self.include(f, header)
        # End with a global definition, in case some compiler
        # doesn't like source files that define nothing.
        # The #undefs are probably unnecessary, but you never know.
        f.write("#undef int\n#undef main\n#undef void\n#undef return\n"
                "int main(void){return 0;}\n")
        f.close()
        return src

    def probe_report(self, header, state, errors, src):
        if not self.debug: return
        sys.stderr.write("%s: %s\n" % (header, state))
        if len(errors) > 1:
            for e in errors:
                sys.stderr.write("| %s\n" % e.strip())
            sys.stderr.write("test code:\n")
            for l in universal_readlines(src):
                sys.stderr.write("| %s\n" % l.strip())
            sys.stderr.write('\n')

    def probe_one(self, header):
        """Probe for one header.  This goes in several stages:

           * First preprocess (cc -E) a source file that just includes
             HEADER.  If this fails, the header is _absent_, and it is
             not added to known_headers.

           * Next compile (cc -c) a source file that just includes HEADER.
             If this succeeds, the header is _correct_, and is added to
             known_headers with value "".

           * Next, if the header has an entry in prerequisites or
             specials, compile (cc -c) a source file with those
             applied.  If that succeeds, the header is _dependent_,
             and is added to known_headers with value "%".

           * Finally, if that too fails, the header is _buggy_, and is
             added to known_headers with value ("!", <error messages>).

           The values set in known_headers are chosen for the
           convenience of report(), which see, and ultimately wind up
           being used by tblgen.py."""
        src = self.gensrc(header, bare=1)
        (rc, errors) = invoke(self.cc + ["-E", src])
        if rc != 0:
            # It's not out of the question that the header exists but
            # needs its prereqs in order to *preprocess* successfully.
            # (Because of #error conditions satisfied by the prereqs,
            # for instance.  Seen for reals on IRIX6.)  Retry that way.
            src = self.gensrc(header, bare=0)
            (rc, perrors) = invoke(self.cc + ["-E", src])
            if rc != 0:
                self.probe_report(header, "absent", errors, src)
                return

        src = self.gensrc(header, bare=1)
        (rc, errors) = invoke(self.cc + ["-c", src])
        if rc == 0:
            self.probe_report(header, "correct", errors, src)
            self.known_headers[header] = ""
            return

        src = self.gensrc(header, bare=0)
        (rc, errors) = invoke(self.cc + ["-c", src])
        if rc == 0:
            self.probe_report(header, "dependent", errors, src)
            self.known_headers[header] = "%"
            return

        self.probe_report(header, "buggy", errors, src)
        self.known_headers[header] = ("!", errors)

    def probe(self):
        """Probe for all the headers in self.headers.  Save the results in
           self.known_headers."""
        self.known_headers = {}
        for h in self.headers:
            self.probe_one(h)

    def smoke(self):
        """Perform a "smoke test": If a probe for stdarg.h fails,
           something is profoundly wrong and we should bail out."""
        src = self.gensrc("stdarg.h", bare=1)
        (rc, errors) = invoke(self.cc + ["-c", src])
        if rc == 0:
            return 1
        sys.stderr.write("error: stdarg.h not detected. Something is wrong "
                         "with your compiler:\n")
        for e in errors:
            sys.stderr.write("# %s\n" % e)
        return 0

    def report(self, f):
        """Write a report on everything we have found to file F."""
        system,release,version = platform_id()
        ccid = compiler_id(self.cc[0])

        f.write("# host: %s %s %s\n" % (system, release, version))
        f.write("# compile command: %s\n" % list2cmdline(self.cc))
        for l in compiler_id(self.cc[0]):
            f.write("## %s\n" % l)

        f.write(":category unknown\n")
        f.write(":label %s\n" % system)
        f.write(":version %s\n" % release)
        f.write(":compiler %s\n" % os.path.basename(self.cc[0]))

        for h in sorthdr(self.known_headers.keys()):
            v = self.known_headers[h]
            if type(v) == type((None,)):
                for err in v[1]:
                    f.write("# %s\n" % err.strip())
                f.write("%s%s\n" % (v[0], h))
            else:
                assert type(v) == type("")
                f.write("%s%s\n" % (v, h))

class ScratchDir:
    """RAII class to create and clean up our scratch directory."""
    def __init__(self):
        # grab these in case __del__ gets called at a bad time
        self.rmtree = shutil.rmtree
        self.cd = os.chdir

        self.oldwd = os.getcwd()
        self.wd = mkdtemp()
        self.cd(self.wd)

    def __del__(self):
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

class Args:
    """Command line argument store."""

    def usage(self, argv0, errmsg=""):
        """Report usage information and exit."""
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
        """Parse the command line."""

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
    try:
        try:
            engine = HeaderProber(args)
            scratch = ScratchDir()
            if not engine.smoke():
                return 1
            engine.probe()
            engine.report(stdout)
            return 0
        except EnvironmentError, e:
            stderr.write("%s: %s\n" % (e.filename, e.strerror))
            return 1
    finally:
        del scratch

if __name__ == '__main__':
    sys.exit(main(sys.argv, sys.stdout, sys.stderr))
