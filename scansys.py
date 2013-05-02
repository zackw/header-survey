#! /usr/bin/env python

# Copyright 2013 Zack Weinberg <zackw@panix.com> and other contributors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# There is NO WARRANTY.


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
# You can also control this script's behavior to some extent with
# command-line options, which must appear before the compiler to use,
# so they aren't confused with arguments to the compiler.  For new
# inventories, you can control all the tags in the file header with
# the options --cattag (-c), --lbltag (-l), --vertag (-v), --cctag
# (-C), and --seqtag (-s).  You can regenerate an old inventory using
# --recheck <FILE>; you're responsible for running this on the correct
# operating system, but it remembers everything else.
#
# The list of headers to look for is taken from the union of all b-
# files in the "data/" directory.  You can override the location of
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
import cgi
import getopt
import os
import re
import sys

# If you make a major change to this program, and it would be
# worthwhile to regenerate all previously-taken inventories with the
# new version, increase this number.
OUTPUT_GENERATION_NO = 1

# suppress all Python warnings, since we deliberately use deprecated
# things (that were the only option in 2.0)
try:
    import warnings
    warnings.simplefilter("ignore")
except:
    pass

# used only for neatness, so the fallback is a stub
# break_on_hyphens was added in 2.6 and the constructor is _not_
# forward compatible
try:
    import textwrap
    def rewrap(text, prefix):
        try:
            return textwrap.fill(text, width=75,
                                 initial_indent=prefix,
                                 subsequent_indent=prefix,
                                 break_long_words=0,
                                 break_on_hyphens=0) + "\n"
        except TypeError:
            return textwrap.fill(text, width=75,
                                 initial_indent=prefix,
                                 subsequent_indent=prefix,
                                 break_long_words=0) + "\n"

except ImportError:
    def rewrap(text, prefix):
        return prefix + text.strip().replace("\n", " ") + "\n"

# used out of an overabundance of caution; falling back to eval with
# no globals or locals is probably safe enough
try:
    from ast import literal_eval
except ImportError:
    def literal_eval(expr):
        return eval(expr, {'__builtins__':{}}, {})

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

# opening a file in "rU" mode on a Python that doesn't support it
# ... silently succeeds!  So we can't use it at all.  Regex time!
_universal_readlines_re = re.compile("\r\n|\r|\n")
def universal_readlines(fname):
    f = open(fname, "rb")
    s = f.read().strip()
    f.close()
    if s == "": return []
    return _universal_readlines_re.split(s)

# We can't use subprocess, it's too new.  We can't use os.popen*,
# because they don't report the exit code.  So... os.system it is.
# Which means we have to shell-quote, which is different on Windows.
# It is convenient to express the platform-specific logic as a
# function which quotes *one* argument; it then works on both Windows
# and Unix to map this function over the argument list and join the
# result list with spaces.
if sys.platform == "win32":
    # We could look for subprocess.list2cmdline, but that only quotes
    # for CreateProcess() [or, rather, the MSVC runtime's
    # CommandLineToArgvW()] whereas what we need is quoting for
    # CommandLineToArgvW *plus* quoting for CMD.EXE, and it turns out
    # that it's easier to do both steps ourselves than to requote what
    # subprocess.list2cmdline returns, because we need to know the
    # boundaries between arguments for both steps.  Code borrowed with
    # extensive modification from Py2.7's subprocess.list2cmdline.
    # See also http://msdn.microsoft.com/en-us/library/17w5ykft.aspx and
    # http://blogs.msdn.com/b/twistylittlepassagesallalike/archive/2011/04/23/everyone-quotes-arguments-the-wrong-way.aspx
    def shellquote1(arg):
        # Phase 1: quote for CommandLineToArgvW.  The only characters
        # that require quotation are space, tab, and double quote.  If
        # any of the above are present, then the whole argument must
        # be surrounded by double quotes, any literal double quotes
        # must be escaped with backslashes, and any backslashes *which
        # immediately precede a double quote* must be escaped with
        # more backslashes.  Note that backslash is *only* significant
        # if it's part of a train of backslashes immediately followed
        # by a double quote. It is technically not necessary to wrap
        # arguments that contain double quotes but *not* spaces or
        # tabs in more double quotes, but it is logically simpler.
        if arg == '':
            qarg = ['"', '"']
        elif (' ' not in arg and '\t' not in arg and '"' not in arg):
            qarg = [c for c in arg]
        else:
            qarg = ['"']
            bs_buf = []
            for c in arg:
                if c == '\\':
                    # Don't know if we need to double yet.
                    bs_buf.append(c)
                elif c == '"':
                    # Double backslashes.
                    qarg.extend(bs_buf)
                    qarg.extend(bs_buf)
                    bs_buf = []
                    qarg.append('\\"')
                else:
                    # Normal char
                    if bs_buf:
                        qarg.extend(bs_buf)
                        bs_buf = []
                    qarg.append(c)

            # Trailing backslashes must be doubled, since the
            # close quote mark immediately follows.
            qarg.extend(bs_buf)
            qarg.extend(bs_buf)
            qarg.append('"')

        # Phase 2: quote for CMD.EXE, for which backslash is *not* a
        # special character but space, tab, double quote, and several
        # other punctuators are.  This process is much simpler: escape
        # each special character with a caret (including caret
        # itself).
        qqarg = []
        for c in qarg:
            if c in ' \t!"%&()<>^|':
                qqarg.append('^')
            qqarg.append(c)
        return ''.join(qqarg)

else: # not Windows; assume os.system is Bourne-shell-like
    try:
        # shlex.quote is the documented API for Bourne-shell
        # quotation, but was only added very recently.
        from shlex import quote as shellquote1
    except (ImportError, AttributeError):
        # pipes.quote is undocumented but has existed all the way back
        # to 2.0.  It is semantically identical to shlex.quote.
        from pipes import quote as shellquote1

def list2shell(seq):
    # Square brackets here required for pre-Python 2.4 compatibility.
    return " ".join([shellquote1(s) for s in seq])

def invoke(argv):
    """Invoke the command in 'argv' and capture its output."""
    # for a wonder, the incantation to redirect both stdout and
    # stderr to a file is exactly the same on Windows as on Unix!
    cmdline = list2shell(argv) + " > htest-out.txt 2>&1"
    msg = [cmdline]
    try:
        rc = os.system(cmdline)
        msg.extend(universal_readlines("htest-out.txt"))
        os.remove("htest-out.txt")
    except EnvironmentError, e:
        if e.filename:
            msg.append("%s: %s" % (e.filename, e.strerror))
        else:
            msg.append("%s: %s" % (argv[0], e.strerror))
    return (rc, msg)

class SysLabel:
    """System information label."""
    def __init__(self, args):
        if args.compiler is not None:
            self.compiler = args.compiler
        else:
            self.compiler = args.cc[0]
        self.ccid = self.compiler_id(args.cc[0])

        if self.ccid.find("Microsoft") != -1:
            self.compile_opt = ["/c", "/Fo", "htest.x"]
            self.preproc_opt = ["/P", "/Fi", "htest.x"]
        else:
            self.compile_opt = ["-S", "-o", "htest.x"]
            self.preproc_opt = ["-E", "-o", "htest.x"]

        system,release,version = self.platform_id()
        if args.unameversion:
            self.hostid = " ".join((system, release, version))
        else:
            self.hostid = " ".join((system, release))

        if args.category is not None:
            self.category = args.category
        else:
            self.category = "unknown"
        if args.label is not None:
            self.label = args.label
        else:
            self.label = system
        if args.version is not None:
            self.version = args.version
        else:
            self.version = version

        self.sequence = args.sequence

    def platform_id(self):
        try:
            import platform
            x = platform.uname()
            return platform.system_alias(x[0], x[2], x[3])
        except (ImportError, AttributeError):
            try:
                x = os.uname()
                return (x[0], x[2], x[3])
            except AttributeError:
                return (sys.platform, "unknown", "unknown")

    _compiler_id_stop_re = re.compile(
        r'unrecognized option|must have argument|not found|warning|error|usage|'
        r'must have argument|copyright|informational note 404|no input files',
        re.IGNORECASE)

    def _compiler_id_1(self, cc, opt):
        # some versions of HP cc won't print their version info unless you
        # give them something to compile, le sigh
        if opt.endswith("dummy.i"):
            made_dummy_i = 1
            f = open("dummy.i", "w")
            f.write("int foo;\n")
            f.close()
        else:
            made_dummy_i = 0

        cmd = [cc] + opt.split()
        (rc, msg) = invoke(cmd)

        if made_dummy_i:
            os.remove("dummy.i")

        results = []
        for l in msg[1:]:
            l = l.strip()
            if l == "": continue
            if self._compiler_id_stop_re.search(l): break
            results.append(l)

        # this lines up with the "# cc: " put on the first line by write()
        return "\n#     ".join(results)

    def compiler_id(self, cc):
        # gcc, clang: --version
        # sun cc, compaq cc, HP CC: -V (possibly with a dummy compilation)
        # mipspro cc: -version
        # xlc: -qversion
        # cl: prints its version number (among other things) upon
        #     encountering any unrecognized invocation
        # -qversion is first because xlc's behavior upon receiving an
        # unrecognized option is to dump out its _entire manpage!_
        for opt in ("-qversion", "--version", "-V", "-version",
                    "-V -c dummy.i"):
            r = self._compiler_id_1(cc, opt)
            if len(r) > 0:
                return r
        return []

    def write(self, f):
        f.write("# host: %s\n" % self.hostid)
        f.write("# cc: %s\n" % self.ccid)
        if self.sequence is not None:
            f.write(":sequence %d\n" % self.sequence)
        f.write(":category %s\n" % self.category)
        f.write(":label %s\n" % self.label)
        f.write(":version %s\n" % self.version)
        f.write(":compiler %s\n" % self.compiler)
        f.write(":gen %s\n" % OUTPUT_GENERATION_NO)

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

def all_prereqs_r(h, prereqs, known, rv):
    """Recursive worker subroutine of all_prereqs (see below)."""

    # don't add a header more than once
    if h in rv: return

    # consider all possible prerequisites of this header even if this
    # version of this header doesn't need them, because prereqs.ini is
    # abbreviated by not listing C->A when C->B and B->A, but C might
    # itself need A even if B doesn't
    for p in prereqs.get(h, []):
        all_prereqs_r(p, prereqs, known, rv)

    # skip headers known to not exist or to be buggy
    if known.get(h, ("!",))[0] == "!": return

    rv.append(h)

def all_prereqs(h, prereqs, known):
    """Produce a list of all the prerequisites of H (from PREREQS),
       recursively, which are known to exist.  Do not include any
       header more than once.  Do not include H itself in the list."""
    rv = []
    all_prereqs_r(h, prereqs, known, rv)
    if len(rv) > 0 and rv[-1] == h: rv.pop()
    return rv

def prereq_combs_r(lo, hi, elts, work, rv):
    """Recursive worker subroutine of prereq_combs (see below)."""
    if lo < hi:
        if lo == 0:
            nlo = 0
        else:
            nlo = work[lo-1] + 1
        for i in xrange(nlo, len(elts)):
            work[lo] = i
            prereq_combs_r(lo+1, hi, elts, work, rv)
    else:
        rv.append([elts[work[i]] for i in xrange(hi)])

def prereq_combs(prereqs):
    """Given an ordered list of header files, PREREQS, that may be
       necessary prior to inclusion of some other header, produce a
       list of all possible subsets of that list, maintaining order.
       (This is not a generator because generators did not exist in
       2.0.  We expect we can get away with generating a list of 2^N
       lists, as len(prereqs) is 4 in the worst case currently known.)
       The list is in "banker's" order as defined in
       http://applied-math.org/subset.pdf -- all 1-element subsets, then
       all 2-element subsets, and so on.  The algorithm is also taken
       from that paper."""
    rv = []
    l = len(prereqs)
    work = [None]*l
    for i in xrange(l+1):
        prereq_combs_r(0, i, prereqs, work, rv)
    return rv

# Annotation generation.
# Annotation lines starting with $ are consumed by tblgen.py and
# attached to the relevant header/OS entry.  They can contain
# arbitrary HTML.
# Annotation lines starting with # are ignored; we use them for
# "raw" error messages needing human editing.

def prereq_ann(prereqs):
    if len(prereqs) == 1:
        rv = "Requires <code>%s</code>." % cgi.escape(prereqs[0])
    elif len(prereqs) == 2:
        rv = ("Requires <code>%s</code> and <code>%s</code>."
                % (cgi.escape(prereqs[0]), cgi.escape(prereqs[1])))
    else:
        rv = "Requires "
        for p in prereqs[:-1]:
            rv += ("<code>%s</code>, " % cgi.escape(p))
        rv += ("and <code>%s</code>." % cgi.escape(prereqs[-1]))
    return rewrap(rv, prefix="$ ")

ecre = re.compile(r'(?s)/\* *(.*?) *\*/')
def special_ann(text):
    m = ecre.search(text)
    if not m: return "$ ???special without explanation???\n"
    return rewrap(m.group(1), prefix="$ ")

def buggy_ann(errors):
    return ("$ PLACEHOLDER: Write an explanation of the problem!\n## "
            + "\n## ".join(errors) + "\n")

class HeaderProber:
    """Engine class - this does all the real work."""

    def __init__(self, args):
        self.debug = args.debug
        self.cc = args.cc
        self.syslabel = SysLabel(args)
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

    def include(self, f, h, dospecial):
        """Subroutine of gensrc, handles one header."""
        s = self.specials.get(h)
        if s is not None and (dospecial or
                              self.known_headers.get(h, ("",))[0] == '%'):
            f.write(s)
        f.write("#include <%s>\n" % (os.path.join(*h.split("/"))))

    def gensrc(self, header, prereqs=[], dospecial=0, trailer=1):
        """Generate a source file that tests the inclusion of HEADER."""
        src = "htest.c"
        f = open(src, "w")

        for p in prereqs:
            self.include(f, p, 0)
        self.include(f, header, dospecial)
        if trailer:
            # End with a global definition, in case some compiler
            # doesn't like source files that define nothing.
            f.write("int main(void){return 0;}\n")
        f.close()
        return src

    def probe_one(self, header):
        """Probe for one header.  This goes in several stages:

           * First, we loop over the sets of possible prerequisites
             provided by prereq_combs(), attempting to compile a
             source file (cc -c) that includes HEADER plus the
             prerequisite set.  If this succeeds, the header is
             considered to be available, and is added to
             known_headers.  If the prerequisite set used was empty,
             the value in known_headers is ("", "") otherwise it is
             ("%", prereq_ann(prereqs)).

             If the header is in the "specials" set, we just try it
             first without, then with, the special text.  If it
             succeeds without the special text, the value in
             known_headers is ("", "") otherwise it is
             ("%", special_ann(special text)).

           * If none of the compilations in stage one succeeded, we
             save the error messages emitted from the compilation with
             the maximal set of prerequisites (conveniently, this is
             always the last compilation) and attempt to preprocess
             (cc -E) a source file containing _only_ "#include <header>".
             If this succeeds, the header is considered to be _buggy_
             and is added to known_headers with value
             ("!", buggy_ann(error messages)).

           * But if that too failed, the header is _absent_ and is not
             added to known_headers.

           The values set in known_headers are chosen for the
           convenience of report(), which see, and ultimately wind up
           being used by tblgen.py."""

        if self.specials.get(header, None) is not None:
            if self.debug:
                sys.stderr.write("%s: trying without special handling\n"
                                 % header)
            src = self.gensrc(header)
            (rc, errors) = invoke(self.cc + self.syslabel.compile_opt + [src])
            if rc == 0:
                self.probe_report(header, "correct", errors, src)
                self.known_headers[header] = ("","")
                os.remove(src)
                os.remove(self.syslabel.compile_opt[-1])
                return

            if self.debug:
                sys.stderr.write("%s: trying with special handling\n"
                                 % header)
            src = self.gensrc(header, dospecial=1)
            (rc, errors) = invoke(self.cc + self.syslabel.compile_opt + [src])
            if rc == 0:
                self.probe_report(header, "dependent", errors, src)
                self.known_headers[header] = \
                    ("%", special_ann(self.specials[header]))
                os.remove(src)
                os.remove(self.syslabel.compile_opt[-1])
                return

        else:
            prereqs = all_prereqs(header, self.prerequisites,
                                  self.known_headers)
            if self.debug:
                sys.stderr.write("%s: possible prereqs %s\n" %
                                 (header, repr(prereqs)))
            # note: the list that prereq_combs() returns is guaranteed
            # to start with [] and end with a list equal to 'prereqs'
            for pc in prereq_combs(prereqs):
                if self.debug:
                    sys.stderr.write("%s: trying prereqs=%s\n" %
                                     (header, repr(pc)))
                src = self.gensrc(header, pc)
                (rc, errors) = invoke(self.cc +
                                      self.syslabel.compile_opt + [src])
                if rc == 0:
                    if len(pc) == 0:
                        self.probe_report(header, "correct", errors, src)
                        self.known_headers[header] = ("","")
                    else:
                        self.probe_report(header, "dependent", errors, src)
                        self.known_headers[header] = ("%", prereq_ann(pc))
                    os.remove(src)
                    os.remove(self.syslabel.compile_opt[-1])
                    return

        # If we get here, all prior trials have failed.  See if we can
        # even preprocess this header.
        src = self.gensrc(header, trailer=0)
        (rc, perrors) = invoke(self.cc + self.syslabel.preproc_opt + [src])
        if rc == 0:
            self.probe_report(header, "buggy", errors, src)
            self.known_headers[header] = ("!", buggy_ann(errors))
            os.remove(self.syslabel.preproc_opt[-1])
            os.remove(src)
        else:
            self.probe_report(header, "absent", perrors, src)
            os.remove(src)

    def probe(self):
        """Probe for all the headers in self.headers.  Save the results in
           self.known_headers."""
        self.known_headers = {}
        for h in self.headers:
            self.probe_one(h)

    def smoke(self):
        """Perform a "smoke test": If a probe for stdarg.h fails,
           something is profoundly wrong and we should bail out."""
        src = self.gensrc("stdarg.h")
        (rc, errors) = invoke(self.cc + self.syslabel.compile_opt + [src])
        os.remove(src)
        if rc != 0:
            sys.stderr.write("error: stdarg.h not detected. Something is wrong "
                             "with your compiler:\n")
            for e in errors:
                sys.stderr.write("# %s\n" % e)
            raise SystemExit(1)
        os.remove(self.syslabel.compile_opt[-1])

    def report(self, f):
        """Write a report on everything we have found to file F."""
        self.syslabel.write(f)
        for h in sorthdr(self.known_headers.keys()):
            v = self.known_headers[h]
            assert type(v) == type((None,))
            f.write("%s%s\n%s" % (v[0], h, v[1]))

class Args:
    """Command line argument store."""

    def usage(self, errmsg=""):
        """Report usage information and exit."""
        if errmsg != "":
            exitcode = 2
            f = sys.stderr
            f.write("%s: %s\n" % (self.argv0, errmsg))
        else:
            exitcode = 0
            f = sys.stdout

        f.write("""\
usage: %s [options] [compiler [args...]]

Determine the set of common header files that are supported by COMPILER.
COMPILER defaults to 'cc'. The inventory is written to stdout, unless
you use --recheck, in which case FILE is overwritten.

options:
  -h, --help           show this help message and exit
  -c, --cattag CAT     set the :category tag in the output
  -l, --lbltag LABEL   set the :label tag in the output
  -v, --vertag VERS    set the :version tag in the output
  -C, --cctag CC       set the :compiler tag in the output
  -s, --seqtag SEQ     set the :sequence tag in the output
  --(no-)uname-version do (not) put `uname -v` in the output (default: yes)
  --recheck FILE       redo the inventory in FILE
  --debug              report all compiler errors
  --datadir DIRECTORY  directory containing lists of header files to probe
  --prereqs FILE       file listing prerequisite sets for each header
"""
                % self.argv0)
        raise SystemExit(exitcode)

    def validate_seqno(self, seqno, warn=0):
        try:
            seqno = int(seqno)
            if 0 <= seqno <= 100:
                return seqno
            raise ValueError
        except ValueError:
            if warn:
                sys.stderr.write("%s: --recheck: bad sequence number '%s' "
                                 "ignored" % (self.argv0, seqno))
                return None
            else:
                self.usage("sequence number must be an integer"
                           "between 0 and 100 (inclusive)" % o)

    def __init__(self, argv):
        """Parse the command line."""

        # defaults
        self.argv0 = os.path.basename(argv[0])
        self.debug = 0
        self.datadir = "data"
        self.prereqs = "prereqs.ini"
        self.output = sys.stdout
        self.recheck = None
        self.cc = ["cc"]
        self.ccset = 0
        self.unameversionset = 0
        self.unameversion = 1
        self.category = None
        self.label = None
        self.version = None
        self.compiler = None
        self.sequence = None

        try:
            opts, args = getopt.getopt(argv[1:], "hc:l:v:C:s:",
                                       ["help", "debug",
                                        "datadir=", "prereqs=", "recheck=",
                                        "cattag=", "lbltag=", "vertag=",
                                        "cctag=", "seqtag=",
                                        "no-uname-version", "uname-version",
                                        ])
        except getopt.GetoptError, e:
            self.usage(str(e))

        for o, a in opts:
            if o == "--datadir":
                self.datadir = a
            elif o == "--prereqs":
                self.prereqs = a
            elif o == "--debug":
                self.debug = 1
            elif o == "--no-uname-version":
                self.unameversionset = 1
                self.unameversion = 0
            elif o == "--uname-version":
                self.unameversionset = 1
                self.unameversion = 1
            elif o == "--recheck":
                self.recheck = a
            elif o in ("-c", "--cattag"):
                self.category = a
            elif o in ("-l", "--lbltag"):
                self.label = a
            elif o in ("-v", "--vertag"):
                self.version = a
            elif o in ("-C", "--cctag"):
                self.compiler = a
            elif o in ("-s", "--seqtag"):
                self.sequence = self.validate_seqno(a)
            elif o in ("-h", "--help"):
                self.usage()
            else:
                self.usage("impossible argument %s %s" % (o, a))

        if len(args) > 0:
            self.ccset = 1
            self.cc = args

        if self.recheck is not None:
            self.prep_recheck()

    def load_tag(self, tag, val):
        cval = getattr(self, tag)
        if cval is None:
            setattr(self, tag, val)
        else:
            sys.stderr.write("%s: --recheck: command line overrides "
                             "%s %s to %s\n"
                             % (self.argv0, tag, repr(val), repr(cval)))

    def prep_recheck(self):
        for l in universal_readlines(self.recheck):
            if len(l) > 0 and l[0] != ':': continue
            (key, rest) = l.split(' ', 1)
            key = key[1:]
            if key == 'sequence':
                self.load_tag(key, self.validate_seqno(rest))
            elif (key == 'category' or
                  key == 'label' or
                  key == 'version' or
                  key == 'compiler'):
                self.load_tag(key, rest)
            elif key == 'unameversion':
                if self.unameversionset:
                    cmd = ['--no-uname-version',
                           '--uname-version'][self.unameversion]
                    tag = ['--no-uname-version',
                           '--uname-version'][int(rest)]
                    sys.stderr.write("%s: --recheck: command line overrides "
                                     "%s to %s" % (self.argv0, cmd, tag))
                else:
                    self.unameversion = int(rest)
            elif key == 'cccmd':
                try:
                    cc = literal_eval(rest)
                    if (type(cc) != type([]) or len(cc) == 0):
                        raise SyntaxError
                    if self.ccset:
                        sys.stderr.write("%s: --recheck: command line "
                                         "overrides compile command "
                                         "'%s' to '%s'"
                                         % (self.argv0, list2shell(cc),
                                            list2shell(self.cc)))
                    else:
                        self.cc = cc
                except (SyntaxError, ValueError):
                    sys.stderr.write("%s: --recheck: bad compile command %s "
                                     "ignored" % (self.argv0, repr(rest)))
        self.recheck = os.path.realpath(self.recheck)
        self.output = open(self.recheck + "-new", "w")

    def finalize(self):
        # tags that would be a distraction if they appeared at the top
        self.output.write("# Additional scansys state below, for --recheck.\n")
        self.output.write(":cccmd %s\n" % repr(self.cc))
        self.output.write(":unameversion %d\n" % self.unameversion)
        self.output.close()
        if self.recheck is not None:
            os.remove(self.recheck + "~") # necessary for Windows, grar
            os.rename(self.recheck, self.recheck + "~")
            os.rename(self.recheck + "-new", self.recheck)

def main():
    args = Args(sys.argv)

    try:
        engine = HeaderProber(args)
        engine.smoke()
        engine.probe()
        engine.report(args.output)
        args.finalize()

    except EnvironmentError, e:
        raise SystemExit("%s: %s" % (e.filename, e.strerror))

if __name__ == '__main__': main()
