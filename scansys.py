#! /usr/bin/env python
# -*- encoding: us-ascii -*-
# vim: set ai ts=4 sw=4 et:

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
# If results are not as expected, --debug will cause the script to
# print extra information about failed probes on stderr.
#
# The list of headers to look for is taken from the union of all b-
# files in the "data/" directory.  You can override the location of
# this directory with --datadir.  There is also a configuration file
# which defines "prerequisites" -- headers which cannot just be
# included in isolation.  This defaults to "prereqs.ini", which can be
# overridden with --prereqs.  Another directory, "decltests/" by
# default, contains C source files which test the contents of each
# header; this can be overridden with --dtestdir.
#
# This script is backward compatible all the way to Python 2.0, and
# therefore uses many constructs which are considered obsolete, and
# avoids many conveniences added after that point.

import ConfigParser
import StringIO
import cgi
import errno
import getopt
import locale
import os
import re
import sys

# If you make a major change to this program, and it would be
# worthwhile to regenerate all previously-taken inventories with the
# new version, increase this number.
# v1 2013-04-20 Exact prereq-set computation
# v2 2013-05-08 Distinguish nonexistent headers from other cpp failures;
#               list all headers in the output file so we can detect the
#               state of having no data about a header
# v3 2013-06-17 Conflicts and declaration checks
OUTPUT_GENERATION_NO = 3

# suppress all Python warnings, since we deliberately use deprecated
# things (that were the only option in 2.0)
try:
    import warnings
    warnings.simplefilter("ignore")
except:
    pass

# on Windows, attempt to suppress "critical error" dialog boxes
# (e.g. missing DLLs) which may pop up from subprocesses.
if sys.platform == 'win32':
    try:
        import ctypes
        # SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX
        ctypes.windll.kernel32.SetErrorMode(0x0001|0x0002|0x8000)
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
                                 break_on_hyphens=0)
        except TypeError:
            return textwrap.fill(text, width=75,
                                 initial_indent=prefix,
                                 subsequent_indent=prefix,
                                 break_long_words=0)

except ImportError:
    def rewrap(text, prefix):
        return prefix + text.strip().replace("\n", " ")

# used out of an overabundance of caution; falling back to eval with
# no globals or locals is probably safe enough
try:
    from ast import literal_eval
except ImportError:
    def literal_eval(expr):
        return eval(expr, {'__builtins__':{}}, {})

# enumerate was added in Python 2.3
if not globals().has_key("enumerate"):
    def enumerate(lst):
        return zip(range(len(lst)), lst)

# It may be necessary to monkey-patch ConfigParser to accept / in an
# option name.  Test . as well.
def maybe_fix_ConfigParser():
    p = ConfigParser.ConfigParser()
    test = StringIO.StringIO("[x]\na.b/c.d=e.f/g.h\n")
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

def platform_id():
    """Return a 3-tuple identifying the host OS to the extent we can
       determine."""
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

# end of old-Python compatibility shims

def fatal(msg, errors=[]):
    """Report a fatal error and exit."""
    sys.stderr.write(rewrap("fatal error: " + msg, "") + "\n")
    for e in errors:
        sys.stderr.write("# %s\n" % e)
    raise SystemExit(1)

def sorted_dict_repr(d):
    """Print what repr(d) would print if it sorted D's keys first.
       Assumes D is a dictionary."""
    ks = d.keys()
    ks.sort()
    return "{%s}" % ", ".join(["%r: %r" % (k, d[k]) for k in ks])

def delete_if_exists(fname):
    """Delete FNAME; do not raise an exception if FNAME already
       doesn't exist.  Used to clean up files that may or may not
       have been created by a compile invocation."""
    try: os.remove(fname)
    except EnvironmentError, e:
        if e.errno != errno.ENOENT:
            raise

# from http://code.activestate.com/recipes/578272-topological-sort/
def toposort(data):
    """Topological sort on DATA, a dictionary whose keys are items
       and whose values are lists of dependent items. Output is a list
       of lists in topological order. The first list consists of items
       with no dependences, each subsequent list consists of items
       that depend upon items in the preceding list.  Order within
       lists is not meaningful."""
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

def hsortkey(h):
    """Sort key generator for sorthdr."""
    segs = h.lower().replace("\\", "/").split("/")
    key = []
    for s in segs:
        key.extend((1, s))
    key[-2] = 0
    return tuple(key)

def sorthdr(hs):
    """Sort a list of pathnames, ASCII case-insensitively.
       All one-component pathnames are sorted ahead of all longer
       pathnames; within a group of multicomponent pathnames with the
       same leading component, all two-component pathnames are sorted
       ahead of all longer pathnames; and so on, recursively."""
    try:
        return sorted(hs, key=hsortkey)
    except NameError:
        # key= and sorted() were both added in 2.4
        # implement the Schwartzian Transform by hand
        khs = [(hsortkey(h), h) for h in hs]
        khs.sort()
        return [x[1] for x in khs]

def toposort_headers(headers, prerequisites):
    """Topologically sort the common-headers list according to the
       prerequisites list, so that gensrc() can safely check whether
       probable-prerequisite headers are known to exist, and include
       them only if so.

       Within each group of headers emitted by the topological sort,
       we sort by the sequence number of the b-file containing the
       header. Within a cluster of headers with the same sequence
       number, we sort by pathname.  (The point of this sorting is
       that conflict detection will ascribe a problem to the second
       of the two headers involved in the conflict, and we want that
       to be the less-standard header, which corresponds to a higher
       sequence number.)
    """
    topo_in = {}
    for h in headers.keys():
        topo_in[h] = prerequisites.get(h, [])
    topo_out = toposort(topo_in)
    rv = []
    try:
        for l in topo_out:
            rv.extend(sorted(l, key=lambda h: (headers[h], hsortkey(h))))
    except NameError:
        # see above re sorted()
        for l in topo_out:
            khs = [(headers[h], hsortkey(h), h) for h in l]
            khs.sort()
            rv.extend([x[2] for x in khs])
    return rv

#
# Compiler invocation.  System identification.
#

def prepare_environment(ccenv):
    """Prepare the environment for compiler invocation."""
    for k, v in ccenv.items():
        os.environ[k] = v

    # Force the locale to "C" both for this process and all subsequently
    # invoked subprocesses.
    for k in os.environ.keys():
        if k[:3] == "LC_" or k[:4] == "LANG":
            del os.environ[k]
    os.environ["LC_ALL"] = "C"
    os.environ["LANGUAGE"] = "C"

    locale.setlocale(locale.LC_ALL, "C")

def invoke(argv):
    """Invoke the command in 'argv' and capture its output."""
    # For a wonder, the incantation to redirect both stdout and
    # stderr to a file is exactly the same on Windows as on Unix!
    # We put the redirections first on the command line because
    # CMD.EXE may include a trailing space in the string it passes
    # to CreateProcess() if they're last.  Yeeeeeah.
    cmdline = ">htest-out.txt 2>&1 " + list2shell(argv)
    msg = [cmdline]
    try:
        rc = os.system(cmdline)
        if rc != 0:
            if sys.platform == 'win32':
                msg.append("[exit %08x]" % rc)
            elif os.WIFEXITED(rc):
                msg.append("[exit %d]" % os.WEXITSTATUS(rc))
            elif os.WIFSIGNALED(rc):
                msg.append("[signal %d]" % os.WTERMSIG(rc))
                # special check for ^C and ^\ (SIGINT, SIGQUIT:
                # respectively signal numbers 2 and 3, everywhere)
                if os.WTERMSIG(rc) == 2 or os.WTERMSIG(rc) == 3:
                    raise KeyboardInterrupt
            else:
                msg.append("[status %08x]" % rc)
        msg.extend(universal_readlines("htest-out.txt"))
        delete_if_exists("htest-out.txt")
    except EnvironmentError, e:
        if e.filename:
            msg.append("%s: %s" % (e.filename, e.strerror))
        else:
            msg.append("%s: %s" % (argv[0], e.strerror))
    return (rc, msg)

def failure_due_to_nonexistence(errors, header):
    """Return true if ERRORS appear to have a root cause of
       HEADER not existing."""
    for e in errors:
        e = e.replace("\\", "/")
        if (e.find(header) != -1 and
            (e.find("No such file or directory") != -1 or
             e.find("cannot find include file") != -1 or
             e.find("Cannot find file") != -1 or
             e.find("cannot open source file") != -1 or
             e.find("Can't open include file") != -1 or
             e.find("is unavailable") != -1 or
             e.find("not found") != -1)):
            return 1
    return 0

def compiler_id(cc):
    stop_re = re.compile(
        r'unrecognized option|must have argument|not found|warning|error|usage|'
        r'must have argument|copyright|informational note 404|no input files',
        re.IGNORECASE)

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
        # some versions of HP cc won't print their version info unless you
        # give them something to compile, le sigh
        if opt.endswith("dummy.i"):
            made_dummy_i = 1
            f = open("dummy.i", "w")
            f.write("int foo;\n")
            f.close()
        else:
            made_dummy_i = 0

        cmd = cc + opt.split()
        (rc, msg) = invoke(cmd)

        if made_dummy_i:
            delete_if_exists("dummy.i")
            delete_if_exists("dummy.o")

        results = []
        for l in msg[1:]:
            l = l.strip()
            if l == "" or l.find("[exit") == 0: continue
            if stop_re.search(l):
                # Special case: GCC's --version message might look like
                # cc (distro x.y.z-w) x.y.z
                # Copyright (C) yyyy Free Software Foundation, Inc.
                # [etc]
                # with the word "GCC" not appearing anywhere.  So if "GCC"
                # doesn't (case insensitively) appear in the text so far,
                # but we just hit the FSF copyright notice, annotate the
                # previous line accordingly.
                if (l.find("Free Software Foundation") != -1
                    and results[-1].find("GCC") == -1
                    and results[-1].find("gcc") == -1):
                    results[-1] = results[-1] + " (GCC)"
                break
            results.append(l)

        # this lines up with the "# cc: " put on the first line by write()
        ccid = "\n#     ".join(results)
        if len(ccid) > 0:
            return ccid
    return "unidentified"

class Metadata:
    """Records all the metadata associated with an inventory.
       Responsible for identifying the OS and compiler, and for
       telling the engine how to invoke the compiler."""

    def __init__(self):
        self.gen          = None
        self.sequence     = None
        self.unameversion = None

        self.ccid         = None
        self.compiler     = None
        self.cccmd        = None
        self.ccenv        = None

        self.hostid       = None
        self.category     = None
        self.label        = None
        self.version      = None

    def write_top(self, f):
        f.write("# host: %s\n" % self.hostid)
        f.write("# cc: %s\n" % self.ccid)
        if self.sequence is not None:
            f.write(":sequence %d\n" % self.sequence)
        f.write(":category %s\n" % self.category)
        f.write(":label %s\n" % self.label)
        f.write(":version %s\n" % self.version)
        f.write(":compiler %s\n" % self.compiler)
        if self.gen is not None and self.gen > 0:
            f.write(":gen %s\n" % self.gen)

    def write_bot(self, f):
        # tags that would be a distraction if they appeared at the top
        f.write("# Additional scansys state below, for --recheck.\n")
        f.write(":cccmd %s\n" % repr(self.cccmd))
        if self.ccenv is not None and len(self.ccenv) > 0:
            f.write(":ccenv %s\n" % sorted_dict_repr(self.ccenv))
        f.write(":unameversion %d\n" % self.unameversion)

    def set_defaults(self):
        if self.unameversion is None: self.unameversion = 1
        if self.gen          is None: self.gen = 0

        system,release,version = platform_id()
        if self.label    is None: self.label = system
        if self.category is None: self.category = "unknown"
        if self.version  is None:
            if self.unameversion:
                self.version = version
            else:
                self.version = release

        if self.unameversion:
            hostid = " ".join((system, release, version))
        else:
            hostid = " ".join((system, release))
        if self.hostid is None:
            self.hostid = hostid
        elif self.hostid != hostid:
            fatal("hostid mismatch: was \"%s\", now \"%s\". "
                  "Are you running --recheck on the right computer?"
                  % (self.hostid, hostid))

        if self.compiler is None: self.compiler = "cc"
        if self.cccmd is None:    self.cccmd = ["cc"]
        if self.ccenv is None:
            self.ccenv = {}
            if sys.platform == "win32":
                # On Windows we need to record a bunch of environment variable
                # settings to make --recheck work, especially with MSVC.
                for ev in ["INCLUDE", "LIB", "LIBPATH", "PATH"]:
                    val = os.environ.get(ev, None)
                    if val is not None: self.ccenv[ev] = val

        # This is the earliest point at which we need to
        # run the compiler.
        prepare_environment(self.ccenv)

        ccid = compiler_id(self.cccmd)
        if self.ccid is None:
            self.ccid = ccid
        elif self.ccid != ccid:
            fatal("ccid mismatch: was \"%s\", now \"%s\". "
                  "Are you running --recheck on the right computer?"
                  % (self.ccid, ccid))

        # Note that these settings rely to some extent on the
        # input file always being named htest.c.
        # If we understand the compiler, we try to put it in
        # C99 strict compliance mode for the "contents" tests.
        # (This unfortunately causes lots of false "buggy" results
        # on the existence tests, so we don't do it there.)
        self.compliance_opt = []
        if self.ccid.find("Microsoft") != -1:
            self.compile_opt = ["/c"]
            self.preproc_opt = ["/P"]
            self.compile_out = "htest.obj"
            self.preproc_out = "htest.i"
        else:
            # Unsuffixed output file used for -E output to make xlc happy.
            # Tru64 cc objects to "-o htest.s" on the theory that you might
            # be overwriting a source file, even though -S by itself
            # will produce htest.s.
            self.compile_opt = ["-S"]
            self.preproc_opt = ["-E", "-o", "htest"]
            self.compile_out = "htest.s"
            self.preproc_out = "htest"

            if (self.ccid.find("GCC") != -1 or
                self.ccid.find("gcc") != -1 or
                self.ccid.find("LLVM") != -1):
                # gcc & llvm are a little _too_ picky with just the
                # first four...
                self.compliance_opt = ["-std=c99", "-pedantic", "-W", "-Wall",
                                       "-Wno-unused", "-Wno-unused-parameter",
                                       "-Wno-unknown-pragmas",
                                       "-Wno-deprecated-declarations",
                                       "-Werror", "-O"]

    def set_internal(self, ctxt, attr, value):
        prev = getattr(self, attr)
        if prev is not None and prev != value:
            if getattr(self, attr + "_ctxt") == "<command line>":
                if ctxt == "<command line>":
                    sys.stderr.write("%s: duplicate '--%s' ignored\n"
                                     % (ctxt, attr))
                else:
                    sys.stderr.write(
                        "%s: previous setting of '%s' overridden "
                        "by command line\n" % (ctxt, attr))
            else:
                sys.stderr.write("%s: duplicate '--%s' ignored\n"
                                 % (ctxt, attr))
        else:
            setattr(self, attr, value)
            setattr(self, attr + "_ctxt", ctxt)

    def set_int(self, ctxt, attr, value, limits=(None, None)):
        try:
            value = int(value)
        except ValueError:
            sys.stderr.write("%s: invalid value for '%s' ignored "
                             "(must be an integer)\n"
                             % (ctxt, attr))
            return
        if limits[0] is not None and value < limits[0]:
            sys.stderr.write("%s: invalid value for '%s' ignored "
                             "(must be >= %d)\n" % (ctxt, attr, limits[0]))
            return
        if limits[1] is not None and value > limits[1]:
            sys.stderr.write("%s: invalid value for '%s' ignored "
                             "(must be <= %d)\n" % (ctxt, attr, limits[1]))
            return
        self.set_internal(ctxt, attr, value)

    def set_parsed(self, ctxt, attr, value, desired_type):
        if type(value) != desired_type:
            try:
                value = literal_eval(value)
            except (SyntaxError, ValueError):
                value = None
        if type(value) != desired_type or len(value) == 0:
                sys.stderr.write("%s: invalid value for '%s' ignored\n"
                                 % (ctxt, attr))
                return
        self.set_internal(ctxt, attr, value)

    def set(self, ctxt, attr, value):
        if attr in ("category", "label", "version", "compiler",
                    "hostid", "ccid"):
            self.set_internal(ctxt, attr, value)
        elif attr == "sequence":
            self.set_int(ctxt, attr, value, (0, 100))
        elif attr == "gen":
            self.set_int(ctxt, attr, value, (0, None))
        elif attr == "unameversion":
            self.set_int(ctxt, attr, value, (0, 1))
        elif attr == "cccmd":
            self.set_parsed(ctxt, attr, value, type([]))
        elif attr == "ccenv":
            self.set_parsed(ctxt, attr, value, type({}))
        else:
            sys.stderr.write("%s: unrecognized metadata tag '%s' ignored\n"
                             % (ctxt, attr))

    def compile_cmd(self, src, compliance=0):
        cmd = self.cccmd + self.compile_opt
        if compliance:
            cmd.extend(self.compliance_opt)
        cmd.append(src)
        return cmd

    def preproc_cmd(self, src):
        return self.cccmd + self.preproc_opt + [src]

#
# Inventory data structure.
#

class Header:
    # state symbols for headers
    # "#", "$", and ":" are used for other purposes
    PRESENT    = ""
    ABSENT     = "-"
    BUGGY      = "!"
    DEPENDENT  = "%"
    CORRECT    = "+"
    INCOMPLETE = "*"
    CORR_DEP   = "@" # correct + prerequisites
    INCO_DEP   = "&" # incomplete + prerequisites

    TAGS = (ABSENT, BUGGY, DEPENDENT, CORRECT, INCOMPLETE,
            CORR_DEP, INCO_DEP)

    TAGINV = { PRESENT    : "PRESENT",
               ABSENT     : "ABSENT",
               BUGGY      : "BUGGY",
               DEPENDENT  : "DEPENDENT",
               CORRECT    : "CORRECT",
               INCOMPLETE : "INCOMPLETE",
               CORR_DEP   : "CORRECT (DEPENDENT)",
               INCO_DEP   : "INCOMPLETE (DEPENDENT)"
             }

    def __init__(self, name, state, avis="", ahid=""):
        self.name  = name
        self.state = state
        self.prereqs = []
        self.special = ""
        self.checked_this_time = 0
        if avis == "":
            self.avis = avis
        else:
            self.avis = "\n" + rewrap(avis, prefix="$ ")
        if ahid == "":
            self.ahid = ""
        else:
            self.ahid = "\n" + rewrap(ahid, prefix="## ")

        if self.state != "" and not (self.state in self.TAGS):
            sys.stderr.write("bogus state for %s: '%s'\n"
                             % (self.name, self.state))
            self.state = self.BUGGY

    def append_avis(self, avis):
        avis = avis.rstrip()
        if avis == "": return
        if self.avis == "":
            self.avis = "\n$ " + avis
        else:
            self.avis = self.avis + "\n$ " + avis

    def append_ahid(self, ahid):
        ahid = ahid.rstrip()
        if ahid == "": return
        if self.ahid == "":
            self.ahid = "\n## " + ahid
        else:
            self.ahid = self.ahid + "\n## " + ahid

    def is_good_state(self):
        return (self.state != self.ABSENT and self.state != self.BUGGY)

    def set_incomplete(self):
        if self.state == self.PRESENT:
            self.state = self.INCOMPLETE
        elif self.state == self.DEPENDENT:
            self.state = self.INCO_DEP

    def set_correct(self):
        if self.state == self.PRESENT:
            self.state = self.CORRECT
        elif self.state == self.DEPENDENT:
            self.state = self.CORR_DEP

    def include(self, f, only_prereqs=0):
        for h in self.prereqs:
            f.write("#include <%s>\n" % (os.path.join(*h.split("/"))))
        f.write(self.special)
        if not only_prereqs:
            f.write("#include <%s>\n" % (os.path.join(*self.name.split("/"))))

    def write(self, f):
        f.write("%s%s%s%s\n" % (self.state, self.name,
                                self.avis, self.ahid))

    def merge(self, other):
        if self.name != other.name:
            fatal("mismatched merge: self.name=%s other.name=%s"
                  % (self.name, other.name))
        if self.state != other.state:
            sys.stderr.write("%s: changed from %s to %s\n"
                             % (self.name,
                                self.TAGINV[self.state],
                                self.TAGINV[other.state]))
            self.state = other.state
        if (other.avis != ""
            and other.avis[:14] != "$ PLACEHOLDER:"
            and self.avis != other.avis):
            if self.avis != "":
                sys.stderr.write(self.name + ": visible annotation changed:\n")
                sys.stderr.write("".join(["-"+l+"\n"
                                          for l in self.avis.split("\n")]))
                sys.stderr.write("".join(["+"+l+"\n"
                                          for l in other.avis.split("\n")]))
            self.avis = other.avis
        if (other.ahid != ""
            and self.ahid != other.ahid):
            if self.ahid != "":
                sys.stderr.write(self.name + ": hidden annotation changed:\n")
                sys.stderr.write("".join(["-"+l+"\n"
                                          for l in self.ahid.split("\n")]))
                sys.stderr.write("".join(["+"+l+"\n"
                                          for l in other.ahid.split("\n")]))
            self.ahid = other.ahid

        if (other.prereqs != []
            and self.prereqs != other.prereqs):
            if self.prereqs != []:
                sys.stderr.write(self.name + ": prerequisites changed:\n")
                sys.stderr.write("".join(["-"+l+"\n"
                                          for l in self.prereqs]))
                sys.stderr.write("".join(["+"+l+"\n"
                                          for l in other.prereqs]))
            self.prereqs = other.prereqs
        if (other.special != ""
            and self.special != other.special):
            if self.special != "":
                sys.stderr.write(self.name + ": special preamble changed:\n")
                sys.stderr.write("".join(["-"+l+"\n"
                                          for l in self.special.split("\n")]))
                sys.stderr.write("".join(["+"+l+"\n"
                                          for l in other.special.split("\n")]))
            self.special = other.special


# Annotation generation.
# Annotation lines starting with $ are consumed by tblgen.py and
# attached to the relevant header/OS entry.  They can contain
# arbitrary HTML.
# Annotation lines starting with # are ignored; we use them for
# "raw" error messages needing human editing.

def ann_prereq(header, prereqs):
    if len(prereqs) == 1:
        ann = "Requires <code>%s</code>." % cgi.escape(prereqs[0])
    elif len(prereqs) == 2:
        ann = ("Requires <code>%s</code> and <code>%s</code>."
               % (cgi.escape(prereqs[0]), cgi.escape(prereqs[1])))
    else:
        ann = "Requires "
        for p in prereqs[:-1]:
            ann += ("<code>%s</code>, " % cgi.escape(p))
        ann += ("and <code>%s</code>." % cgi.escape(prereqs[-1]))

    h = Header(header, Header.DEPENDENT, avis=ann)
    h.prereqs = prereqs
    return h


leading_comment_re = re.compile(r'(?s)/\* *(.*?) *\*/')
def ann_special(header, text):
    m = leading_comment_re.search(text)
    if m:
        m = m.group(1)
    else:
        m = "???special without explanation???"
    h = Header(header, Header.DEPENDENT, avis=m)
    h.special = text
    return h

def ann_buggy(header, errors):
    # This mostly relies on human auditing, but some very common issues
    # have canned messages.
    avis = "PLACEHOLDER: Write an explanation of the problem!"
    if header == "varargs.h":
        for e in errors:
            if e.find("#error") != -1 and e.find("stdarg.h") != -1:
                avis = ("Explicitly unimplemented: contains only an "
                        "<code>#error</code> directive\ntelling the "
                        "programmer to use <code>stdarg.h</code> instead.")
                break

    elif header == "malloc.h":
        for e in errors:
            if e.find("#error") != -1 and e.find("stdlib.h") != -1:
                avis = ("Explicitly unimplemented: contains only an "
                        "<code>#error</code> directive\ntelling the "
                        "programmer to use <code>stdlib.h</code> instead.")
                break
    else:
        pass

    # Preserve the original linebreaking of the error messages.
    # Discard the compiler command line and exit status.
    h = Header(header, Header.BUGGY, avis=avis)
    for e in errors[2:]:
        h.append_ahid(e)
    return h

include_directive_re = re.compile(r'^\s*#\s*include\s*[<"]([^">\n]+)[">]\s*$')
ifndef_re = re.compile(r'^^\s*#\s*ifndef\s+')
class DeclTest:
    """One test of the contents of a header."""

    FEATURE_MACROS = {
        "c89" : "",
        "c99" : "",
        "x5"  : "#define _XOPEN_SOURCE 500\n",
        "x6"  : "#define _XOPEN_SOURCE 600\n",
        "x7"  : "#define _XOPEN_SOURCE 700\n"
    }
    STANDARD_NAMES = {
        "c89" : "ISO C90",
        "c99" : "ISO C99",
        "x5"  : "Single Unix v2",
        "x6"  : "POSIX.1-2001",
        "x7"  : "POSIX.1-2008"
    }

    def __init__(self, fname):
        self.testfile = fname
        self.std = os.path.basename(os.path.dirname(fname))
        self.label = None
        self.header = None
        # We're looking for an optional one-line "label" in a comment
        # (saying what is lacking if the test fails) and then an
        # #include directive naming the header under test.  There
        # might be an #ifndef block around the #include.
        for line in universal_readlines(fname):
            line = line.strip()
            if self.label is None:
                m = leading_comment_re.match(line)
                if m:
                    self.label = m.group(1)
                    continue
            m = include_directive_re.match(line)
            if m:
                self.header = m.group(1)
                break
            if line != "" and not ifndef_re.match(line):
                raise RuntimeError("%s: improperly tagged" % fname)
        assert self.header is not None

    def __cmp__(self, other):
        # If either label is None, it will be sorted to the front,
        # which is what we want.
        return cmp(self.label, other.label)

    def gensrc(self, header):
        assert header.name == self.header
        src = "htest.c"
        f = open(src, "w")
        f.write(self.FEATURE_MACROS[self.std])
        # TESTFILE includes HEADER, but it doesn't include HEADER's
        # prerequisites (if any), so we gotta do that here.
        header.include(f, only_prereqs=1)
        f.write("#include \"%s\"\n" % self.testfile)
        f.close()
        return src

    def note_failure(self, header, errors):
        # If this test has no label, it is the "baseline" requirement
        # for its header, so the header is considered BUGGY.
        std = self.STANDARD_NAMES[self.std]
        if self.label is None:
            header.state = Header.BUGGY
            header.append_avis("Noncompliant with base standard (%s)." % std)
        else:
            header.set_incomplete()
            if (self.label == "features" or
                self.label == "constants" or
                self.label == "types" or
                self.label == "functions"):
                lacking = "PLACEHOLDER: Lacks some %s %s." % (std, self.label)
            elif self.label[:10] == "optional: ":
                lacking = "Lacks %s (optional in %s)" % (self.label[10:], std)
            else:
                lacking = "Lacks %s (%s)" % (self.label, std)
            header.append_avis(lacking)
            for e in errors[2:]:
                header.append_ahid(e)

class Dataset:
    """Holds all the data collected over the course of one run."""
    def __init__(self, metadata):
        self.headers  = {}
        self.metadata = metadata
        self.from_scratch = 1

    def read(self, fname):
        self.from_scratch = 0
        last_header = None
        hashstrip_re = re.compile(r"^#+ ?")
        dollarstrip_re = re.compile(r"^\$+ ?")
        ccid = ""
        for i, l in enumerate(universal_readlines(fname)):
            l = l.rstrip()
            if l == "": continue
            if l[0] == ":":
                (key, rest) = l.split(" ", 1)
                key = key[1:]
                self.metadata.set("%s:%d" % (fname, i), key, rest)

            elif l[0] == "#":
                if l == "# Additional scansys state below, for --recheck.":
                    pass
                elif l[:8] == "# host: ":
                    self.metadata.set("%s:%d" % (fname, i), "hostid", l[8:])
                elif l[:6] == "# cc: ":
                    self.metadata.set("%s:%d" % (fname, i), "ccid", l[6:])
                elif l[:6] == "#     " and self.metadata.ccid is not None:
                    self.metadata.ccid = self.metadata.ccid + "\n" + l
                elif last_header is not None:
                    last_header.append_ahid(hashstrip_re.sub("", l))
                else:
                    sys.stderr.write("%s:%d: unclaimed '#' line\n"
                                     % (fname, i))

            elif l[0] == "$":
                if last_header is not None:
                    last_header.append_avis(dollarstrip_re.sub("", l))
                else:
                    sys.stderr.write("%s:%d: unclaimed '$' line\n"
                                     % (fname, i))

            else:
                state = ""
                if l[0] in Header.TAGS:
                    state = l[0]
                    l = l[1:]
                if self.headers.has_key(l):
                    sys.stderr.write("%s:%d: duplicate header '%s'\n"
                                     % (fname, i, l))
                    last_header = None
                else:
                    self.headers[l] = last_header = Header(l, state)

    def record(self, header):
        if self.headers.has_key(header.name):
            if self.from_scratch:
                fatal("why did we probe %s twice?" % header.name)
            self.headers[header.name].merge(header)
        else:
            self.headers[header.name] = header
        self.headers[header.name].checked_this_time = 1

    def write(self, f):
        self.metadata.write_top(f)
        for h in sorthdr(self.headers.keys()):
            self.headers[h].write(f)
        self.metadata.write_bot(f)

#
# Prerequisite generation.
#

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
    if (not known.has_key(h) or
        known[h].state == Header.BUGGY or
        known[h].state == Header.ABSENT):
        return

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

# Main probe logic.

class HeaderProber:
    """Engine class - this does all the real work."""

    def __init__(self, metadata, args):
        self.metadata = metadata
        self.debug = args.debug
        self.read_prereqs(args.prereqs)
        self.read_headers(args.datadir)
        self.read_decltests(args.dtestdir)

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
                seqno = 50
                for l in universal_readlines(join(datadir, fn)):
                    l = l.strip()
                    if l[:10] == ":sequence ":
                        seqno = int(l[10:])
                        continue
                    elif l == "" or l[0] in ":#":
                        continue
                    headers[l] = seqno

        self.headers = toposort_headers(headers, self.prerequisites)

    def read_decltests(self, dtestdir):
        """Read the contents of the decltests directory, which contains
           test programs for many of the headers we probe."""
        decltests = {}
        for dirpath, dirnames, filenames in os.walk(dtestdir):
            for fn in filenames:
                if fn[-2:] != ".c": continue
                try:
                    test = DeclTest(os.path.join(dirpath, fn))
                except RuntimeError, e:
                    # skip improperly tagged tests with a warning
                    sys.stderr.write(str(e) + "\n")
                    continue
                if not decltests.has_key(test.header):
                    decltests[test.header] = []
                decltests[test.header].append(test)

        for l in decltests.values():
            l.sort()
            assert len(l) >= 1
            # some test groups have no baseline, so we don't insist
            # that l[0].label is None, but we do insist that if there
            # is more than one test, at most one of them is the baseline.
            if len(l) >= 2 and l[1].label is None:
                sys.stderr.write("%s: inconsistent declaration tests\n"
                                 % l[0].header)
                del decltests[l[0].header]

        self.decltests = decltests

    def probe_report(self, header, state, errors, src):
        """Report the results of one probe on stderr.
           Only active in --debug mode."""
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
        if dospecial:
            s = self.specials.get(h)
            if s is not None:
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

    def smoke(self):
        """Perform a "smoke test": if these tests fail, something is
           profoundly wrong and we should bail out."""

        # We should be able to detect the presence of stdarg.h.
        src = self.gensrc("stdarg.h")
        (rc, errors) = invoke(self.metadata.compile_cmd(src))
        self.probe_report("stdarg.h", "smoke, exit %d" % rc, errors, src)
        delete_if_exists(src)
        delete_if_exists(self.metadata.compile_out)
        if rc != 0:
            fatal("stdarg.h not detected. Something is wrong "
                  "with your compiler:", errors)

        # We should be able to detect the absence of nonexistent.h.
        src = self.gensrc("nonexistent.h")
        (rc, errors) = invoke(self.metadata.preproc_cmd(src))
        self.probe_report("nonexistent.h", "smoke, exit %d" % rc, errors, src)
        delete_if_exists(src)
        delete_if_exists(self.metadata.preproc_out)
        if rc == 0:
            fatal("'#include <nonexistent.h>' preprocessed "
                  "with successful exit code. Something is wrong with "
                  "how we are invoking your compiler.", errors)
        if not failure_due_to_nonexistence(errors, "nonexistent.h"):
            fatal("Failed to confirm nonexistence of <nonexistent.h>. "
                  "This probably means scansys.py doesn't understand your "
                  "compiler. Diagnostics were: ", errors)

    def probe(self, dataset):
        """Probe for all the headers in self.headers.  Save the results in
           DATASET."""

        for h in self.headers:
            try:
                hh = self.probe_existence(h, dataset)
                if hh.is_good_state():
                    self.probe_conflict(hh, dataset)
                if hh.is_good_state():
                    self.probe_contents(hh)
                dataset.record(hh)
            finally:
                delete_if_exists("htest.c")
                delete_if_exists(self.metadata.preproc_out)
                delete_if_exists(self.metadata.compile_out)

        # Dataset is now updated to the current generation.
        dataset.metadata.gen = OUTPUT_GENERATION_NO

    def probe_existence(self, header, dataset):
        """Probe for the existence of one header.  This goes in
           several stages:

           * First, we loop over the sets of possible prerequisites
             provided by prereq_combs(), attempting to compile a
             source file (cc -c) that includes HEADER plus the
             prerequisite set.  If this succeeds without any
             prerequisites, the header is _present_; if it succeeds
             with some nonempty set of prerequisites, the header is
             _dependent_.

             If the header is in the "specials" set, we just try it
             first without, then with, the special text.  If it
             succeeds without the special text it's present, if it
             succeeds with, it's dependent.

           * If none of the compilations in stage one succeeded, we
             save the error messages emitted from the compilation with
             the maximal set of prerequisites (conveniently, this is
             always the last compilation) and attempt to preprocess
             (cc -E) a source file containing _only_ "#include <header>".
             If this succeeds, or if it fails and
             failure_due_to_nonexistence(errors, header) is false, the
             header is _buggy_.

           * Otherwise the header is _absent_.

           Returns a Header object recording the state of the header.
           For dependent headers, this also remembers the special text
           or prerequisite set, and for buggy headers it remembers the
           error messages.
        """

        if self.specials.get(header, None) is not None:
            if self.debug:
                sys.stderr.write("%s: trying without special handling\n"
                                 % header)
            src = self.gensrc(header)
            (rc, errors) = invoke(self.metadata.compile_cmd(src))
            if rc == 0:
                self.probe_report(header, "present", errors, src)
                return Header(header, Header.PRESENT)

            if self.debug:
                sys.stderr.write("%s: trying with special handling\n"
                                 % header)
            src = self.gensrc(header, dospecial=1)
            (rc, errors) = invoke(self.metadata.compile_cmd(src))
            if rc == 0:
                self.probe_report(header, "dependent", errors, src)
                return ann_special(header, self.specials[header])

        else:
            prereqs = all_prereqs(header, self.prerequisites,
                                  dataset.headers)
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
                (rc, errors) = invoke(self.metadata.compile_cmd(src))
                if rc == 0:
                    if len(pc) == 0:
                        self.probe_report(header, "present", errors, src)
                        return Header(header, Header.PRESENT)
                    else:
                        self.probe_report(header, "dependent", errors, src)
                        return ann_prereq(header, pc)

        # If we get here, all prior trials have failed.  See if we can
        # even preprocess this header.
        src = self.gensrc(header, trailer=0)
        (rc, perrors) = invoke(self.metadata.preproc_cmd(src))
        if rc == 0 or not failure_due_to_nonexistence(perrors, header):
            self.probe_report(header, "buggy", errors, src)
            return ann_buggy(header, errors)
        else:
            self.probe_report(header, "absent", perrors, src)
            return Header(header, Header.ABSENT)

    def probe_conflict(self, header, dataset):
        """Determine whether HEADER conflicts with any other header which
           is known to exist -- that is, whether you cannot include HEADER
           and some other header at the same time."""

        # N.B. We don't log successes here (even in debug mode),
        # because it's much too verbose.  We do, however, report that
        # we are in this phase for each header (in debug mode),
        # because it is quite slow, potentially involving O(N^2)
        # compiler invocations.
        if self.debug:
            sys.stderr.write("%s: checking for conflicts\n"
                             % header.name)

        # Primarily as a performance optimization, we first check this
        # header against *all* other already-validated headers.  Only if
        # that fails do we go one by one looking for the actual conflict.
        # This also means we're more likely to detect complex conflicts
        # involving more than two headers.
        src = "htest.c"
        f = open(src, "w")
        for other in dataset.headers.values():
            # Skip other-headers which are known to be absent or buggy.
            #
            # Also (if we are rechecking) skip other-headers which
            # have not yet been checked on this scan, as they will not
            # have the correct prerequisite annotations and the tests will
            # spuriously fail.
            #
            # Also specifically skip other-header == this-header, but
            # then at the very end, include this-header twice to
            # confirm that you can do that.
            if (not other.checked_this_time or
                other.state == Header.ABSENT or
                other.state == Header.BUGGY or
                other.name == header.name):
                continue
            other.include(f)
        header.include(f)
        header.include(f)
        f.write("int main(void){return 0;}\n")
        f.close()
        (rc, all_errors) = invoke(self.metadata.compile_cmd(src))
        if rc == 0:
            if self.debug:
                sys.stderr.write("%s: no conflicts\n" % header.name)
            return

        # If we get to this point, there is *some* kind of conflict and we
        # need to figure out what.
        self.probe_report(header.name, "buggy", all_errors, src)
        if self.debug:
            sys.stderr.write("%s: conflict detected, investigating...\n"
                             % header.name)
        found_conflict = 0
        for other in dataset.headers.values() + [header]:
            if (not other.checked_this_time or
                other.state == Header.ABSENT or
                other.state == Header.BUGGY or
                (other is not header and other.name == header.name)):
                continue
            src = "htest.c"
            f = open(src, "w")
            other.include(f)
            header.include(f)
            f.write("int main(void){return 0;}\n")
            f.close()

            (rc, errors) = invoke(self.metadata.compile_cmd(src))
            if rc != 0:
                self.probe_report(header.name, "buggy", errors, src)
                if other.name == header.name:
                    header.append_avis("Can't be included twice in the same "
                                       "source file.")
                else:
                    header.append_avis("Can't be used together with "
                                       "<code>%s</code>."
                                       % cgi.escape(other.name))
                for e in errors[2:]:
                    header.append_ahid(e)
            found_conflict = 1

        if not found_conflict:
            # The conflict is not as simple as not being able to include
            # some pair of headers together.  The human editor will have
            # to figure it out.
            header.append_avis("PLACEHOLDER: Complex conflict, "
                               "needs investigation")
            for e in all_errors[2:]:
                header.append_ahid(e)

        # We knew this for some time now, but only set it at the end to
        # prevent perturbation of the above logic.
        header.state = Header.BUGGY

    def probe_contents(self, header):
        if not self.decltests.has_key(header.name):
            return
        ok = 1
        for test in self.decltests[header.name]:
            src = test.gensrc(header)
            if self.debug:
                sys.stderr.write("%s: testing contents (%s)\n"
                                 % (header.name, test.testfile))
            (rc, errors) = invoke(self.metadata.compile_cmd(src, compliance=1))
            if rc == 0:
                if self.debug:
                    sys.stderr.write("%s: test passed\n" % header.name)
            else:
                ok = 0
                if test.label is None: tag = "buggy"
                else:                  tag = "incomplete"
                self.probe_report(header.name, tag, errors, src)
                test.note_failure(header, errors)
                # don't bother with further tests if the baseline fails
                if test.label is None:
                    break
        if ok:
            header.set_correct()

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
  --dtestdir DIRECTORY directory containing declaration tests for each header
  --prereqs FILE       file listing prerequisite sets for each header
"""
                % self.argv0)
        raise SystemExit(exitcode)

    def __init__(self, argv, metadata):
        """Parse the command line."""

        # defaults
        self.argv0 = os.path.basename(argv[0])
        self.debug = 0
        self.datadir = "data"
        self.dtestdir = "decltests"
        self.prereqs = "prereqs.ini"
        self.output = sys.stdout
        self.recheck = None

        try:
            opts, args = getopt.getopt(argv[1:], "hc:l:v:C:s:",
                                       ["help", "debug", "recheck=",
                                        "datadir=", "dtestdir=", "prereqs=",
                                        "cattag=", "lbltag=", "vertag=",
                                        "cctag=", "seqtag=",
                                        "no-uname-version", "uname-version",
                                        ])
        except getopt.GetoptError, e:
            self.usage(str(e))

        for o, a in opts:
            if o == "--datadir":
                self.datadir = a
            if o == "--dtestdir":
                self.dtestdir = a
            elif o == "--prereqs":
                self.prereqs = a
            elif o == "--debug":
                self.debug = 1
            elif o == "--recheck":
                self.recheck = a

            elif o == "--no-uname-version":
                metadata.set("<command line>", "unameversion", 0)
            elif o == "--uname-version":
                metadata.set("<command line>", "unameversion", 1)
            elif o in ("-c", "--cattag"):
                metadata.set("<command line>", "category", a)
            elif o in ("-l", "--lbltag"):
                metadata.set("<command line>", "label", a)
            elif o in ("-v", "--vertag"):
                metadata.set("<command line>", "version", a)
            elif o in ("-C", "--cctag"):
                metadata.set("<command line>", "compiler", a)
            elif o in ("-s", "--seqtag"):
                metadata.set("<command line>", "sequence", a)
            elif o in ("-h", "--help"):
                self.usage()
            else:
                self.usage("impossible argument %s %s" % (o, a))

        if len(args) > 0:
            metadata.set("<command line>", "cccmd", args)

        if self.recheck is not None:
            self.output = open(self.recheck + "-new", "w")

    def finalize(self):
        self.output.close()
        if self.recheck is not None:
            # necessary for Windows, grar
            delete_if_exists(self.recheck + "~")

            os.rename(self.recheck, self.recheck + "~")
            os.rename(self.recheck + "-new", self.recheck)

def main():
    metadata = Metadata()
    args = Args(sys.argv, metadata)
    dataset = Dataset(metadata)
    if args.recheck is not None:
        dataset.read(args.recheck)
    metadata.set_defaults()

    engine = HeaderProber(metadata, args)
    engine.smoke()
    engine.probe(dataset)

    dataset.write(args.output)
    args.finalize()

if __name__ == '__main__': main()
