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
# header files are present on your operating system.  It also probes
# for conflicts among the headers, and for those headers whose
# contents are defined by the C or POSIX standards, it checks for
# missing declarations.
#
# For detailed instructions on how to run this script, see
# doc/inventories.md.
#
# WARNING: This script is not feature complete yet; you can't actually
# take an inventory as described in inventories.md.
#
# NOTE: This script is backward compatible all the way to Python 2.0,
# and therefore uses many constructs which are considered obsolete,
# and avoids many conveniences added after that point.

import ConfigParser
import StringIO
import errno
import glob
import locale
import os
import random
import re
import string
import sys

# "True" division only became available in Python 2.2.  Therefore, it is a
# style violation to use bare / or // anywhere in this program other than
# via these wrappers.  Note that "from __future__ import division" cannot
# be written inside a try block, and that without the "exec", the
# SyntaxError won't get caught.
try:
    exec "def floordiv(n,d): return n // d"
except SyntaxError:
    def floordiv(n,d): return n / d
def truediv(n,d): return float(n) / float(d)

# It may be necessary to monkey-patch ConfigParser to accept / in an option
# name and/or : in a section name.  Also test empty values (not to be confused
# with the absence of a value, i.e. no : or = at all).
def maybe_fix_ConfigParser():
    p = ConfigParser.ConfigParser()
    test = StringIO.StringIO("[x:y/z.w]\na.b/c.d=\n")
    try:
        p.readfp(test)
    except ConfigParser.ParsingError:
        if (not getattr(ConfigParser.ConfigParser, 'SECTCRE')
            or not getattr(ConfigParser.ConfigParser, 'OPTCRE')):
            raise # we don't know what to do
        # this is taken verbatim from 2.7
        ConfigParser.ConfigParser.SECTCRE = re.compile(
            r'\['                        # [
            r'(?P<header>[^]]+)'         # very permissive!
            r'\]'                        # ]
            )
        # this is slightly modified from 2.7 to work around different
        # behavior in 2.0's regular expression engine
        ConfigParser.ConfigParser.OPTCRE = re.compile(
            r'(?P<option>[^:=\s]+)'      # very permissive!
            r'\s*(?P<vi>[:=])\s*'        # any number of space/tab,
                                         # followed by separator
                                         # (either : or =), followed
                                         # by any # space/tab
            r'(?P<value>.*)$'            # everything up to eol
            )
        p = ConfigParser.ConfigParser()
        test.seek(0)
        p.readfp(test)
maybe_fix_ConfigParser()

def group_matched(grp):
    """True if 'grp', the return value of re.MatchObject.group(),
       represents a successfully matched group.  At some point in the 2.x
       series, match.group(N) changed from returning -1 to returning None
       if the group was part of an unmatched alternative.  Also reject the
       empty string (this can be returned on a successful match, but is
       never what we want in context)."""
    return grp is not None and grp != -1 and grp != ""

def delete_if_exists(fname):
    """Delete FNAME; do not raise an exception if FNAME already
       doesn't exist.  Used to clean up files that may or may not
       have been created by a compile invocation."""
    if fname is None or fname == "":
        return
    try:
        os.remove(fname)
    except EnvironmentError, e:
        if e.errno != errno.ENOENT:
            raise

_universal_readlines_re = re.compile("\r\n|\r|\n")
def universal_readlines(fname):
    """Replacement for the Python 2.3+ "universal newlines" feature in open().
       Doesn't even try to use "rU" because opening a file in that mode
       silently succeeds (but does not do what one wants) on older Pythons."""
    f = open(fname, "rb")
    s = f.read().strip()
    f.close()
    if s == "": return []
    return _universal_readlines_re.split(s)

def named_tmpfile(prefix="tmp", suffix="txt"):
    """Create a scratch file, with a unique name, in the current directory.
       Returns the name of the scratch file, which exists, but is not open.
       Caller is responsible for cleaning up.  8.3 compliant if caller
       provides no more than three-character prefixes and suffixes.

       2.0 `tempfile` does not have NamedTemporaryFile, and doesn't have
       anything useful for defining it, either.  This is kinda sorta like
       the code implementing 2.7's NamedTemporaryFile."""
    symbols = "abcdefghijklmnopqrstuvwxyz01234567890"
    tries = 0
    while 1:
        candidate = "".join([random.choice(symbols) for _ in (1,2,3,4,5)])
        path = prefix + candidate + "." + suffix
        try:
            os.close(os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0600))
            return path
        except EnvironmentError, e:
            if e.errno != errno.EEXIST:
                raise
            # The code above can generate 60,466,176 different names,
            # but give up after ten thousand iterations; we don't want
            # to spend hours looping if something is genuinely wrong.
            tries += 1
            if tries == 10000:
                raise
            # otherwise loop

# Process invocation helpers.
# We can't use subprocess, it's too new.  We can't use os.popen*, because
# they don't report the exit code.  So... os.system it is.  Which means we
# have to shell-quote, which is different on Windows.  It is convenient to
# express the platform-specific logic as a function which quotes *one*
# argument; it then works on both Windows and Unix to map this function
# over the argument list and join the result list with spaces.
#
# We don't use subprocess.list2cmdline for the Windows case because it only
# quotes for [the MSVC runtime's] CommandLineToArgvW(), whereas what we need
# is quoting for CommandLineToArgvW *plus* quoting for CMD.EXE, and it
# turns out that it's easier to do both steps ourselves than to requote
# what subprocess.list2cmdline returns, because we need to know the
# boundaries between arguments for both steps.  Code borrowed with
# extensive modification from Py2.7's subprocess.list2cmdline.  See also
# http://msdn.microsoft.com/en-us/library/17w5ykft.aspx and
# http://blogs.msdn.com/b/twistylittlepassagesallalike/archive/2011/04/23/everyone-quotes-arguments-the-wrong-way.aspx

if sys.platform == "win32":
    def shellquote1(arg):
        """Quote one subprocess argument to survive passage through
           CMD.EXE and CommandLineToArgvW (in that order)."""

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

else:
    # not Windows; assume os.system is Bourne-shell-like
    try:
        # shlex.quote is the documented API for Bourne-shell quotation, but
        # is only available in 3.3 and later.  We try to import it anyway,
        # despite that this program has no hope of running correctly under
        # 3.x; who knows, maybe there will be a 2.8 that has it.
        from shlex import quote as shellquote1
    except (ImportError, AttributeError):
        # pipes.quote is undocumented but has existed all the way back
        # to 2.0.  It is semantically identical to shlex.quote.
        from pipes import quote as shellquote1

def list2shell(argv):
    """Given an arbitrary argument vector (including the command name)
       return a string which can be passed to os.system to execute that
       command as execvp() would have, i.e. all shell metacharacters are
       neutralized."""
    # Square brackets here required for pre-Python 2.4 compatibility.
    return " ".join([shellquote1(arg) for arg in argv])

#
# utility routines that aren't workarounds for old Python
#

def plural(n):
    """Return the appropriate English suffix for N items.
       Use like so: "%d item%s" % (n, plural(n))."""
    if n == 1: return ""
    return "s"

def english_boolean(s):
    s = s.strip().lower()
    if s == "yes" or s == "on" or s == "true" or s == "1":
        return 1
    if s == "no" or s == "off" or s == "false" or s == "0":
        return 0
    raise RuntimeError("'%s' is not recognized as true or false" % s)

def splitto(string, sep, fields):
    """Split STRING at instances of SEP into exactly FIELDS fields."""
    exploded = string.split(sep, fields-1)
    if len(exploded) < fields:
        exploded.extend([""] * (fields - len(exploded)))
    return exploded

def not_a_subset(l, m):
    """Return true if L is nonempty and not a subset of M."""
    if not l: return 0
    if not m: return 1
    for x in l:
        for y in m:
            if x is y: break
        else:
            return 1
    return 0

squishwhite_re = re.compile(r"\s+")
def squishwhite(s):
    """Remove leading and trailing whitespace from S, and collapse each
       segment of internal whitespace within S to a single space."""
    return squishwhite_re.sub(" ", s.strip())

def hsortkey(h):
    """Sort key generator for sorthdr."""
    segs = str(h).lower().replace("\\", "/").split("/")
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

def dependency_combs_r(lo, hi, elts, work, rv):
    """Recursive worker subroutine of dependency_combs (see below)."""
    if lo < hi:
        if lo == 0:
            nlo = 0
        else:
            nlo = work[lo-1] + 1
        for i in xrange(nlo, len(elts)):
            work[lo] = i
            dependency_combs_r(lo+1, hi, elts, work, rv)
    else:
        rv.append([elts[work[i]] for i in xrange(hi)])

def dependency_combs(deps):
    """Given an ordered list of header files, DEPS, that may be
       necessary prior to inclusion of some other header, produce a
       list of all possible subsets of that list, maintaining order.
       (This is not a generator because generators did not exist in
       2.0.  We expect we can get away with generating a list of 2^N
       lists, as len(deps) is 4 in the worst case currently known.)
       The list is in "banker's" order as defined in
       http://applied-math.org/subset.pdf -- all 1-element subsets,
       then all 2-element subsets, and so on.  The algorithm is also
       taken from that paper."""
    rv = []
    l = len(deps)
    work = [None]*l
    for i in xrange(l+1):
        dependency_combs_r(0, i, deps, work, rv)
    return rv

def subst_filename(fname, opts):
    """If any of OPTS is of the form '$.extension', replace the
       dollar sign with FNAME's base name.  Returns the modified
       string or list."""
    (base, _) = os.path.splitext(fname)
    if type(opts) == type(""):
        if opts.startswith("$."):
            return base + opts[1:]
        else:
            return opts
    else:
        nopts = []
        for opt in opts:
            if opt.startswith("$."):
                nopts.append(base + opt[1:])
            else:
                nopts.append(opt)
        return nopts

#
# Logging
#

class Logger:
    """Logger is a singleton class which owns the log file and the
       terminal (to which progress reports will be written).  Logger
       is also responsible for adjusting the standard streams and the
       environment for safe subprocess invocation, and for tracking
       whether an error has occurred (i.e. inventory-taking has failed
       and we should exit unsuccessfully, but not necessarily right
       this instant)."""

    def __init__(self, log_fname, verbose, progress):
        self.logf = open(log_fname, "w")
        self.verbose = verbose
        self.progress = progress
        self.need_cr = 0
        self.error_occurred = 0

        # Force the locale to "C" both for this process and all
        # subsequently invoked subprocesses.
        for k in os.environ.keys():
            if k[:3] == "LC_" or k[:4] == "LANG":
                del os.environ[k]
        os.environ["LANG"] = "C"
        os.environ["LANGUAGE"] = "C"
        os.environ["LC_ALL"] = "C"
        locale.setlocale(locale.LC_ALL, "C")

        # Rejigger standard I/O streams. After this operation, file
        # descriptor 0 reads from /dev/null, whereas descriptors 1 and
        # 2 write to /dev/null; sys.stdin is closed; and sys.stdout
        # and sys.stderr have been replaced with new file objects
        # writing to wherever they used to write to, but with their
        # underlying file descriptors moved above 2.  The point of
        # this exercise is to ensure that processes invoked via
        # os.system (see above) cannot interfere with our output or
        # get stuck trying to read from our input.  (The output part
        # is defense-in-depth, as they are always invoked with
        # explicit output redirections.)  The interpreter cannot be
        # persuaded to close the C-level stdin, stdout, or stderr
        # objects, but they shouldn't get used after this point.

        try:
            devnull = os.devnull
        except AttributeError:
            if sys.platform == "win32":
                devnull = "nul"
            else:
                devnull = "/dev/null"

        ifd = os.open(devnull, os.O_RDONLY)
        sys.stdin.close()
        sys.__stdin__.close()
        os.dup2(ifd, 0)
        os.close(ifd)

        ofd = os.open(devnull, os.O_WRONLY)
        orig_stdout = os.dup(1)
        sys.stdout = os.fdopen(orig_stdout, "w")
        sys.__stdout__ = sys.stdout
        os.dup2(ofd, 1)

        orig_stderr = os.dup(2)
        sys.stderr = os.fdopen(orig_stderr, "w")
        sys.__stderr__ = sys.stderr
        os.dup2(ofd, 2)
        os.close(ofd)

    def log(self, msg, output=[]):
        """Write MSG to the log file, followed by OUTPUT if any.
           Expected use pattern is for OUTPUT to be the contents of a file
           as returned by universal_readlines(), e.g. code about to be
           compiled, or error messages coming back.  Forces a carriage
           return after MSG and after each element of OUTPUT."""
        self.logf.write(msg.rstrip())
        self.logf.write('\n')
        for line in output:
            self.logf.write(("| %s" % line).rstrip())
            self.logf.write('\n')
        self.logf.flush()

    def begin_test(self, msg):
        """Announce the commencement of a test, both in the log file and
           on stderr."""
        msg = msg.strip()
        self.log("Begin test: %s" % msg)
        if self.progress:
            sys.stderr.write(msg)
            sys.stderr.write("..")
            sys.stderr.flush()
            self.need_cr = 1

    def progress_tick(self):
        """Indicate on stderr that forward progress is being made.
           Should normally be paired with one or more calls to log()."""
        if self.progress:
            sys.stderr.write(".")
            sys.stderr.flush()
            self.need_cr = 1

    def progress_note(self, msg):
        """Indicate status in the middle of an ongoing test.
           MSG is sent both to stderr and to the logfile, and a carriage
           return is forced before and after MSG if necessary."""
        msg = msg.strip()
        self.log(msg)
        if self.progress:
            if self.need_cr:
                sys.stderr.write("\n")
            sys.stderr.write(msg)
            sys.stderr.write("\n")
            sys.stderr.flush()
            self.need_cr = 0

    def end_test(self, msg):
        """Announce the completion of a test, both in the log file
           and on stderr."""
        msg = msg.strip()
        self.log("Test complete: %s" % msg)
        if self.progress:
            sys.stderr.write(" %s\n" % msg)
            sys.stderr.flush()
            self.need_cr = 0

    def error(self, msg):
        """Announce an error severe enough that we cannot produce
           meaningful output, but not so severe that we must abandon
           the test run immediately."""
        msg = "Error: %s" % msg
        self.log(msg)
        if self.need_cr:
            sys.stderr.write("\n")
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        self.need_cr = 0
        self.error_occurred = 1

    def fatal(self, msg):
        """Announce an error severe enough that the test run should
           be aborted immediately.  Does not return."""
        msg = "Fatal error: %s" % msg
        self.log(msg)
        if self.need_cr:
            sys.stderr.write("\n")
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        raise SystemExit(1)

    def invoke(self, argv):
        """Invoke the command in ARGV, capturing and logging all its
           output and its exit code."""
        # For a wonder, the incantation to redirect both stdout and
        # stderr to a file is exactly the same on Windows as on Unix!
        # We put the redirections first on the command line because
        # CMD.EXE may include a trailing space in the string it passes
        # to CreateProcess() if they're last.  Yeeeeeah.
        rc = -1
        msg = []
        result = None
        try:
            try:
                result = named_tmpfile(prefix="out", suffix="txt")
                cmdline = ">" + result + " 2>&1 " + list2shell(argv)
                msg.append(cmdline)
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
                msg.extend(universal_readlines(result))
            except EnvironmentError, e:
                if e.filename:
                    msg.append("%s: %s" % (e.filename, e.strerror))
                else:
                    msg.append("%s: %s" % (argv[0], e.strerror))
        finally:
            delete_if_exists(result)

        self.log(msg[0], msg[1:])
        return (rc, msg)

#
# Code generation for decltests (used by Header.test_contents, far below)
#

idchars = string.letters + string.digits + "_"
def mkdeclarator(dtype, name):
    """Construct a 'declarator' -- a C expression which declares NAME as an
       object of type DTYPE.  Relies on manual annotation to know where to
       put the name: if there is a dollar sign somewhere in DTYPE, that is
       replaced with the name, otherwise the name is tacked on the end."""
    ds = splitto(dtype, "$", 2)
    if name == "": # for function prototypes with argument name omitted
        return ds[0] + ds[1]
    elif ds[0][-1] in idchars:
        return ds[0] + " " + name + ds[1]
    else:
        return ds[0] + name + ds[1]

def mk_pointer_to(dtype):
    """Given a C type expression DTYPE, return the expression for a pointer
       to that type.  Uses the same annotation convention as above: if there
       is a dollar sign somewhere in DTYPE, a star is inserted immediately
       before it, otherwise it is tacked on the end."""
    ds = splitto(dtype, "$", 2)
    if ds[0][-1] == "*" or ds[0][-1] == " ":
        rv = ds[0] + "*"
    else:
        rv = ds[0] + " *"
    if ds[1] == "":
        return rv
    else:
        return rv + "$" + ds[1]

def crunch_fncall(val):
    """Given a function specification, VAL, of the form

         RTYPE ":" ARGTYPE ["," ARGTYPE]... ["..." ARGTYPE ["," ARGTYPE]...]

       extract and return, as a tuple, in this order, the variable parts
       of the definition of a function that will call this function:

         * the function's return type expression
         * the function's prototype expression (that is, a list of argument
           types -- without function-call parentheses)
         * a prototype expression for the *definition* of a function that
           will call the function (i.e. including the optional arguments
           and giving formal parameter names)
         * a call expression for the function (just the part that goes
           inside the function-call parentheses)
         * whether or not to put "return " before the function call.

       See TestFunctions and TestFnMacros for usage."""

    (rtype, argtypes) = splitto(val, ":", 2)
    rtype = rtype.strip()
    argtypes = argtypes.strip()
    if argtypes == "" or argtypes == "void":
        argtypes = "void"
        argdecl = "void"
        call = ""
    else:
        mandatory, rest = splitto(argtypes, ", ...", 2)
        argtypes = [x.strip() for x in mandatory.split(",")]
        if len(rest) > 0:
            calltypes = argtypes[:]
            argtypes.append("...")
            calltypes.extend([x.strip() for x in rest.split(",")])
        else:
            calltypes = argtypes

        argtypes = ", ".join([mkdeclarator(x, "") for x in argtypes])

        call = []
        argdecl = []
        for t, v in zip(calltypes, string.letters[:len(calltypes)]):
            if len(t) >= 7 and t[:5] == "expr(" and t[-1] == ")":
                call.append(t[5:-1])
            else:
                call.append(v)
                argdecl.append(mkdeclarator(t, v))
        call = ", ".join(call)
        argdecl = ", ".join(argdecl)

    if rtype == "" or rtype == "void":
        return_ = ""
    else:
        return_ = "return "
    return (rtype, argtypes, argdecl, call, return_)

class TestItem:
    """Base class for individual content test cases.

       Test items have a _tag_ which should correspond to the symbol being
       tested, plus a _standard_ and _module_ which categorize the symbol
       (see content_tests/CATEGORIES.ini).  They all start out _enabled_, and
       tests which fail are disabled until all remaining tests pass; the
       set of disabled tests corresponds to the set of unavailable or
       incorrectly defined symbols.  Finally, the _meaning_ may be one of
       self.MISSING (if this test fails, the symbol is not defined at all);
       self.INCORRECT (if this test fails, the symbol is defined
       incorrectly); or self.AMBIGUOUS (if this test fails, the symbol is
       either unavailable or incorrect; we can't tell which).

       Each test is generated on exactly one line, so that we don't have
       to understand compiler errors beyond the line they're on."""

    MISSING   = 'M'
    INCORRECT = 'W'
    AMBIGUOUS = 'X'

    def __init__(self, infname, std, mod, tag, meaning):
        """Subclasses will need to extend this constructor to save
           information about the specific thing being tested."""
        self.infname = infname
        self.std = std
        self.mod = mod
        self.tag = tag
        self.meaning = meaning
        self.enabled = 1
        self.name = None
        self.lineno = None

    def generate(self, out):
        """Public interface to append the code for this test to OUT.
           Subclasses should not need to tamper with this method."""
        if not self.enabled: return
        lineno = len(out) + 1
        if self.name is None:
            self.lineno = lineno
            self.name = "t_" + str(self.lineno)
        else:
            if self.lineno < lineno:
                raise RuntimeError("%s (%s:%s): line numbers out of sync "
                                   " (want %d, already at %d)"
                                   % (self.tag, self.std, self.mod,
                                      self.lineno, lineno))
            out.extend([""] * (self.lineno - lineno))
        self._generate(out)

    def _generate(self, out):
        """Subclasses must override this stub method to emit the actual
           code for their test case."""
        raise NotImplementedError

class TestDecl(TestItem):
    """Test item which works by declaring a global variable with a
       specific type, possibly with an initializer, possibly wrapped in an
       #if or #ifdef conditional."""

    def __init__(self, infname, std, mod, tag, meaning,
                 dtype, init="", cond=""):
        TestItem.__init__(self, infname, std, mod, tag, meaning)

        self.dtype = squishwhite(dtype)
        self.init = squishwhite(init)
        self.cond = squishwhite(cond)

    def _generate(self, out):
        decl = mkdeclarator(self.dtype, self.name)
        if self.cond != "":
            if self.cond[0] == '?':
                out.append("#if %s" % self.cond[1:])
            else:
                out.append("#ifdef %s" % self.cond)
        if self.init == "":
            out.append(decl + ";")
        else:
            out.append("%s = %s;" % (decl, self.init))
        if self.cond != "":
            out.append("#endif")

class TestFn(TestItem):
    """Test item which works by defining a function with a particular
       return type, argument list, and body.  If the body is empty, the
       function is just declared, not defined.

       Note that if all three optional arguments are empty, what you get is
       "void t_NNN(void);" which isn't particularly useful."""

    def __init__(self, infname, std, mod, tag, meaning,
                 rtype="", argv="", body=""):
        TestItem.__init__(self, infname, std, mod, tag, meaning)

        self.rtype = squishwhite(rtype)
        self.argv = squishwhite(argv)
        self.body = squishwhite(body)

        if self.rtype == "": self.rtype = "void"
        if self.argv == "": self.argv = "void"
        if self.body != "" and self.body[-1] != ";":
            self.body = self.body + ";"

    def _generate(self, out):
        # To declare a function that returns a function pointer without
        # benefit of typedefs, you write
        #   T (*fn(ARGS))(PROTO) { ... }
        # where ARGS are the function's arguments, and PROTO is
        # the *returned function pointer*'s prototype.
        name = "%s(%s)" % (self.name, self.argv)
        decl = mkdeclarator(self.rtype, name)
        if self.body == "":
            out.append(decl + ";")
        else:
            out.append("%s { %s }" % (decl, self.body))

class TestCondition(TestItem):
    """Test item which verifies that an integer constant expression, EXPR,
       evaluates to a nonzero value.  EXPR need not be valid in #if.
       If COND is nonempty, the expression test is wrapped in an #if
       or #ifdef conditional."""

    def __init__(self, infname, std, mod, tag, meaning,
                 expr, cond=""):
        TestItem.__init__(self, infname, std, mod, tag, meaning)
        self.expr = squishwhite(expr)
        self.cond = squishwhite(cond)

    def _generate(self, out):
        if self.cond != "":
            if self.cond[0] == '?':
                out.append("#if %s" % self.cond[1:])
            else:
                out.append("#ifdef %s" % self.cond)
        out.append("extern char %s[(%s) ? 1 : -1];"
                   % (self.name, self.expr))
        if self.cond != "":
            out.append("#endif")

class TestComponent:
    """Base class for blocks of tests, all of the same general type
       (test for functions, test for constants, etc).

       Test components have a _standard_ and _module_ (same meaning as
       for individual items) and a set of individual test _items_.  On
       entry to the constructor, the ITEMS argument is simply a dictionary
       of strings taken verbatim from the test definition; they will be
       converted to appropriate subclasses of TestItem for storage in
       self.items (which is *not* a dictionary)."""

    def __init__(self, infname, std, mod, items):
        self.infname = infname
        self.std = std
        self.mod = mod
        self.items = []
        self.preprocess(items)

    def preprocess(self, items):
        """Interpret the complete list of items.  Subclasses may override
           this method if necessary."""
        for k, v in items.items():
            if len(k) >= 5 and k[:2] == "__" and k[-2:] == "__":
                self.pp_special(k, v)
            else:
                self.pp_normal(k, v)

    def pp_normal(self, k, v):
        """Subclasses must override this method.  Interpret the key-value
           pair (K, V) -- normally K will be the name of a symbol to test
           for, and V will describe it somehow -- and add appropriate
           TestItems to self.items."""
        raise NotImplementedError

    def pp_special(self, k, v):
        """Keys which begin and end with `__` are reserved for special
           purposes.  Subclasses may override this function if they define
           their own special keys, but must in that case call this one on
           any special key they don't define."""

        # currently there are no globally-meaningful special keys
        raise RuntimeError("%s [functions:%s:%s]: "
                           "invalid or misused key '%s'"
                           % (self.infname, self.std, self.mod, k))

    def generate(self, out):
        """Emit code for each test item."""
        for item in self.items:
            item.generate(out)
        out.append("")

    def disabled_items(self):
        rv = []
        for item in self.items:
            if not item.enabled:
                rv.append(item)
        return rv

class TestTypes(TestComponent):
    """Test presence and correctness of type definitions."""

    label = "types"

    def pp_normal(self, k, v):
        d = " ".join(k.split("."))
        if v.endswith(" struct"):
            d = "struct " + d
            v = v[:-7]

        # To test for the basic presence of a type name, attempt to declare
        # a function that takes a pointer to that type as part of its
        # argument list.  Unlike most other constructs that depend only on
        # the presence of a (possibly-incomplete) type name, this works
        # even to detect undeclared struct tags.  (Anything you do with an
        # undeclared struct tag will forward-declare it as a side effect,
        # so it's basically impossible to get the compiler to error out by
        # using one.  But if this happens inside a prototype argument list,
        # the tag is scoped only to that declaration, so both gcc and clang
        # issue a warning, which is good enough for our purposes.)
        self.items.append(TestFn(self.infname, self.std, self.mod,
                                 tag=k, meaning=TestItem.MISSING,
                                 argv=mk_pointer_to(d)))

        # Test correctness by attempting to declare a variable of the
        # specified type with an appropriate initializer.
        #
        # ??? Can we do better about enforcing scalar type categories
        #     (signed/unsigned/integral/floating)?

        if v == "opaque":
            # Just test that a local variable of this type can be declared.
            self.items.append(TestDecl(self.infname, self.std, self.mod,
                                       tag=k, meaning=TestItem.INCORRECT,
                                       dtype=d))
        elif v == "incomplete":
            # We've already tested this as much as we can.
            pass
        else:
            if v == "signed":
                init = "-1"
            elif v == "unsigned" or v == "integral" or v == "arithmetic":
                init = "1"
            elif v == "floating":
                init = "1.0f"
            elif v == "scalar":
                init = "0"
            elif len(v) >= 7 and v[:5] == "expr(" and v[-1] == ")":
                init = v[5:-1]
            else:
                raise RuntimeError("%s [types:%s:%s]: %s: "
                                   "unimplemented type category %s"
                                   % (self.infname, self.std, self.mod,
                                      k, v))

            self.items.append(TestDecl(self.infname, self.std, self.mod,
                                       tag=k, meaning=TestItem.INCORRECT,
                                       dtype=d, init=init))

class TestFields(TestComponent):
    """Test presence and correctness of structure fields."""

    label = "fields"

    def pp_normal(self, k, v):
        (typ, field) = splitto(k, ".", 2)
        if field == "":
            raise RuntimeError("%s [fields:%s:%s]: %s: missing field name"
                               % (self.infname, self.std, self.mod, k))
        # "s_TAG" is shorthand for "struct TAG", as "option" names
        # cannot contain spaces; similarly, "u_TAG" for "union TAG"
        if typ[:2] == "s_": typ = "struct " + typ[2:]
        if typ[:2] == "u_": typ = "union " + typ[2:]

        # To test whether a field exists, attempt to take a pointer to it.
        # To test whether the field has the correct type, attempt to return
        # that pointer without casting it.
        argv=mkdeclarator(mk_pointer_to(typ), "xx")
        addressop = "&"
        if v.endswith("[]"):
            v = v[:-2]
            addressop = ""

        # Explicitly cast to void to avoid warnings.
        self.items.append(TestFn(self.infname, self.std, self.mod,
                                 tag=k, meaning=TestItem.MISSING,
                                 rtype="void *", argv=argv,
                                 body="return (void *)%sxx->%s"
                                 % (addressop, field)))

        # If the type is not precisely specified, attempt to set the
        # field to 0 instead of taking a pointer.
        if v == "integral" or v == "arithmetic":
            self.items.append(TestFn(self.infname, self.std, self.mod,
                                     tag=k, meaning=TestItem.INCORRECT,
                                     rtype="void", argv=argv,
                                     body="xx->" + field + " = 0"))
        else:
            self.items.append(TestFn(self.infname, self.std, self.mod,
                                     tag=k, meaning=TestItem.INCORRECT,
                                     rtype=mk_pointer_to(v), argv=argv,
                                     body="return %sxx->%s"
                                     % (addressop, field)))


dollar_re = re.compile(r"\$")
class TestConstants(TestComponent):
    """Test presence and correctness of symbolic constants."""

    label = "constants"

    def pp_normal(self, k, v):
        # Constants may be conditionally defined; notably, X/Open
        # specifies lots of these in limits.h and unistd.h.  To
        # handle this, when the value starts with "ifdef:", we
        # wrap #ifdef NAME ... #endif around each test.  It can
        # also start with "if CONDITION:" which case we wrap
        # #if CONDITION ... #endif around each test.  Note that in
        # the latter case, CONDITION may not contain a colon.
        cond = ""
        if v.startswith("ifdef:"):
            cond = k
            v = v[6:]
        elif v.startswith("if "):
            colon = v.find(":")
            if colon == -1:
                raise RuntimeError("%s [constants:%s:%s]: %s: "
                                   "ill-formed #if expression"
                                   % (self.infname, self.std, self.mod, k))
            cond = '?'+v[3:colon]
            v = v[(colon+1):]

        # If 'k' starts with a dollar sign, it is not a real
        # constant name; 'v' is an expression to be tested
        # literally.
        if k.startswith("$"):
            self.items.append(TestCondition(self.infname, self.std, self.mod,
                                            tag=k, meaning=TestItem.INCORRECT,
                                            expr=v, cond=cond))
            return

        # Optional test for value correctness.  (We do this first as it
        # works out how to do the presence test as a side-effect.)
        # 'v' may start with a type in square brackets.
        if v.startswith("["):
            (t, v) = v.split("]", 1)
            t = t[1:]
            v = v.strip()
        else:
            t = None

        # If 'v' contains dollar signs, each of them is replaced with 'k'
        # (the constant name) to form the expression to test; or if it
        # starts with a relational operator, 'k' is inserted before the
        # operator.
        if v.find("$") != -1:
            self.items.append(TestCondition(self.infname, self.std,
                                            self.mod, tag=k,
                                            meaning=TestItem.INCORRECT,
                                            expr=dollar_re.sub(k, v),
                                            cond=cond))
            if t is None: t = "int"

        elif (v.find(">") != -1 or v.find("<") != -1
              or v.find("=") != -1):
            self.items.append(TestCondition(self.infname, self.std,
                                            self.mod, tag=k,
                                            meaning=TestItem.INCORRECT,
                                            expr=k + " " + v,
                                            cond=cond))
            if t is None: t = "int"

        else:
            if t is None: t = v
            if t == "": t = "int"

        # Test for presence (with the correct type).
        if t == "str":
            self.items.append(TestDecl(self.infname, self.std, self.mod,
                                       tag=k, meaning=TestItem.MISSING,
                                       dtype="const char $[]",
                                       init = "\"\"" + k + "\"\"",
                                       cond=cond))
        else:
            self.items.append(TestDecl(self.infname, self.std, self.mod,
                                       tag=k, meaning=TestItem.MISSING,
                                       dtype=t, init=k,
                                       cond=cond))

class TestGlobals(TestComponent):
    """Test presence and correctness of global variables."""

    label = "globals"

    def pp_normal(self, k, v):
        if v == "": v = "int"
        # does it exist?
        self.items.append(TestDecl(self.infname, self.std, self.mod,
                                   tag=k, meaning=TestItem.MISSING,
                                   dtype="extern const char "
                                   "$[sizeof(%s)]" % k))
        # does it have the correct type?
        self.items.append(TestFn(self.infname, self.std, self.mod,
                                 tag=k, meaning=TestItem.INCORRECT,
                                 rtype=v, body="return " + k))

class TestSpecialDecls(TestComponent):
    """Test ability to make specific declarations; basically allows direct
       use of TestDecl.  Intended for cases where the name of interest
       isn't a typename or constant.  For instance: _Complex, _Alignas,
       _Atomic, _Thread_local (type qualifiers); CMPLX, _Alignof
       (initializer expressions)."""

    label = "special"

    def pp_normal(self, k, v):
        (dtype, init) = splitto(v, "=", 2)
        self.items.append(TestDecl(self.infname, self.std, self.mod,
                                   tag=k, meaning=TestItem.AMBIGUOUS,
                                   dtype=dtype, init=init))


class TestFunctions(TestComponent):
    """Test presence and correctness of function declarations."""

    label = "functions"

    def pp_normal(self, k, v):
        (rtype, argtypes, argdecl, call, return_) = crunch_fncall(v)

        # Each function is tested three ways.  The most stringent test is
        # to declare a function pointer with its exact (should-be)
        # prototype and set it equal to the function name.  This will
        # sometimes fail because of acceptable variation between the
        # standard and the system, so we also test that we can call the
        # function passing arguments of the expected types.  That test is
        # done twice, once suppressing any macro definition, once not.
        self.items.append(TestDecl(self.infname, self.std, self.mod,
                                   tag=k, meaning=TestItem.INCORRECT,
                                   dtype = rtype + " (*$)("+argtypes+")",
                                   init = k))
        self.items.append(TestFn(self.infname, self.std, self.mod,
                                 tag=k, meaning=TestItem.INCORRECT,
                                 rtype = rtype,
                                 argv  = argdecl,
                                 body  = "%s(%s)(%s);" % (return_, k, call)))
        self.items.append(TestFn(self.infname, self.std, self.mod,
                                 tag=k, meaning=TestItem.MISSING,
                                 rtype = rtype,
                                 argv  = argdecl,
                                 body  = "%s%s(%s);" % (return_, k, call)))

class TestFnMacros(TestComponent):
    """Test presence and correctness of function-like macros."""

    label = "fn_macros"

    def pp_normal(self, k, v):
        (rtype, argtypes, argdecl, call, return_) = crunch_fncall(v)

        # Function-like macros can only be tested by calling them in
        # the usual way.
        self.items.append(TestFn(self.infname, self.std, self.mod,
                                 tag=k, meaning=TestItem.AMBIGUOUS,
                                 rtype = rtype,
                                 argv  = argdecl,
                                 body  = "%s%s(%s);" % (return_, k, call)))

class TestSpecial(TestComponent):
    """Test a special construct.  Use when you need precise control over
       the entirety of a function definition in order to test something.
       Can also test several things at once, which is useful when they
       can only be used together.  This is what you want for e.g.
       pthread_cleanup_push/pop, va_start/va_arg/va_end."""

    label = "special"

    # There are two usage patterns, both of which make extensive
    # use of special keys; it is easier to override preprocess()
    # and do all the work there.
    def preprocess(self, items):
        pitems = {}
        argv  = items.get("__args__", "")
        rtype = items.get("__rtype__", "")

        if items.has_key("__tested__"):
            if not items.has_key("__body__"):
                raise RuntimeError("%s [special:%s:%s]: section incomplete"
                                   % (self.infname, self.std, self.mod))
            for k in items.keys():
                if (k != "__args__" and
                    k != "__rtype__" and
                    k != "__tested__" and
                    k != "__body__"):
                    TestComponent.pp_special_key(self, k, items[k])

            tag = items["__tested__"]
            body = items["__body__"]
            tfn = TestFn(self.infname, self.std, self.mod,
                         tag=tag, meaning=TestItem.AMBIGUOUS,
                         rtype=rtype, argv=argv, body=body)
            for t in tag.split():
                self.items.append(tfn)
        else:
            for k,v in items.items():
                if (k == "__args__" or k == "__rtype__"): continue
                if len(k) > 5 and k[:2] == "__" and k[-2:] == "__":
                    TestComponent.pp_special_key(self, k, v)
                else:
                    vx = v.split(":", 1)
                    if len(vx) == 2:
                        tfn = TestFn(self.infname, self.std, self.mod,
                                     tag=k, meaning=TestItem.AMBIGUOUS,
                                     rtype=vx[0], argv=argv, body=vx[1])
                    else:
                        tfn = TestFn(self.infname, self.std, self.mod,
                                     tag=k, meaning=TestItem.AMBIGUOUS,
                                     rtype=rtype, argv=argv, body=v)
                    self.items.append(tfn)

    # We also need to override generate() to handle a single TestFn
    # object being in the list more than once.  (This _could_ be
    # hoisted to the superclass, but it's only needed here.)
    def generate(self, out):
        items = self.items
        enabled = [item.enabled for item in items]
        for item in items:
            item.generate(out)
            item.enabled = 0
        for item, e in zip(items, enabled):
            item.enabled = e

class TestProgram:
    """A complete test program for a particular header.  Responsible for
       top-level parsing of the .ini file, and for tracking tests that
       have been disabled."""

    # Map labels in the .ini file to TestComponent subclasses.
    COMPONENTS = {
        "types"         : TestTypes,
        "fields"        : TestFields,
        "constants"     : TestConstants,
        "globals"       : TestGlobals,
        "functions"     : TestFunctions,
        "fn_macros"     : TestFnMacros,
        "special"       : TestSpecial,
        "special_decls" : TestSpecialDecls,
    }

    def __init__(self, fname):
        """Construct a TestProgram from an .ini file, FNAME."""
        self.header = None
        self.baseline = None
        self.line_index = None
        self.global_decls = ""
        self.infname = fname
        self.extra_includes = []
        for k in self.COMPONENTS.keys():
            setattr(self, k, [])
        self.std_index = {}

        self.load(fname)

    def load(self, fname):
        """Read FNAME and add its contents to self.  This is separate from
           __init__ so it can be called recursively (see load_preamble)."""

        # We would like to use RawConfigParser but that wasn't available
        # in 2.0, so instead we always use get() with raw=1.
        spec = ConfigParser.ConfigParser()
        spec.optionxform = lambda x: x # make option names case sensitive
        spec.read(fname)

        # Most section headers in the .ini file have internal structure:
        # "[" COMPONENT ":" STANDARD [ ":" MODULE ] "]"
        # where COMPONENT is one of the keys of self.COMPONENTS, above,
        # and STANDARD and MODULE are defined in content_tests/CATEGORIES.ini.
        # (FIXME: Issue errors for unknown STANDARD and MODULE.)
        # The exception is [preamble], which has no annotations.
        # Parse all section headers and dispatch to the appropriate
        # TestComponent constructor.
        for sect in spec.sections():
            what, std, mod = splitto(sect, ":", 3)
            items = {}
            for k in spec.options(sect):
                items[k] = spec.get(sect, k, raw=1)

            if what == "preamble":
                if std != "" or mod != "":
                    raise RuntimeError("%s: [preamble] section cannot be "
                                       "annotated" % fname)
                self.load_preamble(fname, items)

            elif std == "":
                raise RuntimeError("%s: [%s] section must be annotated "
                                   "with a standard"
                                   % (fname, what))
            else:
                if not self.std_index.has_key(std):
                    self.std_index[std] = {}
                if not self.std_index[std].has_key(mod):
                    self.std_index[std][mod] = []

                component = self.COMPONENTS[what](fname, std, mod, items)
                getattr(self, what).append(component)
                self.std_index[std][mod].append(component)

    def load_preamble(self, fname, items):
        """Parse the special [preamble] section."""
        if self.header is None:
            self.header = items["header"]
        del items["header"]

        if self.baseline is None:
            self.baseline = items["baseline"]
        del items["baseline"]

        if items.has_key("global"):
            if self.global_decls != "":
                self.global_decls = self.global_decls + "\n" + items["global"]
            else:
                self.global_decls = items["global"]
            del items["global"]

        if items.has_key("extra_includes"):
            self.extra_includes.extend(items["extra_includes"].split())
            del items["extra_includes"]

        if items.has_key("includes"):
            for h in items["includes"].split():
                if h.endswith(".h"): h = h[:-2]
                h = "_".join(h.split("/")) + ".ini"
                self.load(os.path.join(os.path.dirname(fname), h))
            del items["includes"]

        if len(items) > 0:
            raise RuntimeError("%s: unrecognized [preamble] items: %s"
                               % (fname, ", ".join(items.keys())))

    # WARNING: The next four methods can only be used after generate() has
    # been called at least once.
    def disable_line(self, line, log):
        """Disable the test case at line LINE (or just before it -- necessary
           for #if(def)-wrapped test cases)."""
        oline = line
        while not self.line_index.has_key(line):
            line -= 1
            if line == 0:
                log.fatal("Nothing to disable at line %d of content test.  "
                          "(Problem with preamble? Check %s.)"
                          % (oline, self.infname))
        item = self.line_index[line]
        assert item.lineno == line
        if not item.enabled: return None
        item.enabled = 0
        return item.tag

    def all_disabled(self):
        """True if every test case in this program has been disabled."""
        for item in self.line_index.values():
            if item.enabled:
                return 0
        return 1

    def disabled_tags(self):
        """Return a list of all the tags for disabled test cases."""
        tags = []
        for item in self.line_index.values():
            if not item.enabled:
                tags.append(item.tag)
        return tags

    def results(self, cfg):
        """Serialize the results of a content test, and reset the tester."""
        rv = ContentTestResult(self, cfg)
        for item in self.line_index.values():
            item.enabled = 1
        return rv

    def generate(self, out):
        """Append the test program to OUT.
           WARNING: Caller is responsible for emitting an #include of the
           header under test (and all its dependencies) *before* calling
           this function."""

        # If all tests are disabled, and the header under test contains
        # nothing but macros, we could trip over the requirement that a
        # translation unit contain at least one top-level definition or
        # declaration (C99 6.9 -- implicit in the grammar; the
        # "translation-unit" production does not accept an empty token
        # sequence).
        out.append("int avoid_empty_translation_unit;")

        if self.global_decls != "":
            out.extend(self.global_decls.split("\n"))
            out.append("")

        # We have to list each category explicitly because they need to
        # happen in a particular order.
        for c in self.types:         c.generate(out)
        for c in self.fields:        c.generate(out)
        for c in self.constants:     c.generate(out)
        for c in self.globals:       c.generate(out)
        for c in self.special_decls: c.generate(out)

        # Extra includes are to provide any types that are necessary
        # to formulate function calls: e.g. stdio.h declares functions
        # that take a va_list argument, but doesn't declare va_list
        # itself.  They happen at this point because they can spoil
        # tests for types, fields, constants, and globals.
        if self.extra_includes:
            for h in self.extra_includes:
                out.append("#include <%s>" % h)
            out.append("")

        for c in self.functions: c.generate(out)
        for c in self.fn_macros: c.generate(out)
        for c in self.special:   c.generate(out)

        # Now that we've generated the entire file, construct an index of
        # what's at what line.  This is what enables use of the three
        # methods above (disable_line, all_disabled, disabled_tags).
        if self.line_index is None:
            self.line_index = {}
            for bloc in self.COMPONENTS.keys():
                for group in getattr(self, bloc):
                    for item in group.items:
                        self.line_index[item.lineno] = item

#
# Compilation
#

class CompilationMode:
    """The 'mode' in which a header is being tested.  Right now, this is
       just a pair of booleans: conformance yes/no, threads yes/no."""
    def __init__(self, conform=0, thread=0):
        self.conform = conform
        self.thread = thread

    def __str__(self):
        c = "."
        t = "."
        if self.conform: c = "c"
        if self.thread: t = "t"
        return "["+c+t+"]"

class Compiler:
    """A Compiler instance knows how to invoke a particular compiler
       on provided source code.  The Metadata class, below, does most
       of the heavy lifting on figuring out what *kind* of compiler it is.

       Because we are limited to os.system for subprocess invocation,
       and because some compilers require particular environment
       variable settings, it does not work to have more than one
       Compiler instance per process."""

    def __init__(self, base_cmd, cfg, log):
        self.base_cmd = base_cmd
        self.log = log

        self.notfound_re = re.compile(cfg.notfound_re, re.VERBOSE)
        self.errloc_re   = re.compile(cfg.errloc_re, re.VERBOSE)

        self.preproc_cmd = cfg.preproc.split()
        self.preproc_out = cfg.preproc_out
        self.compile_cmd = cfg.compile.split()
        self.compile_out = cfg.compile_out

        self.define_opt  = cfg.define
        self.thread_opt  = cfg.threads.split()
        self.dump_macros = cfg.dump_macros.split()

        self._is_cross_compiler = None

    def failure_due_to_nonexistence(self, msg, header):
        """True if MSG contains an error message indicating that HEADER
           does not exist."""
        for m in msg:
            if self.notfound_re.search(m) and m.find(header) != -1:
                return 1
        return 0

    def is_cross_compiler(self):
        """True if this is a cross compiler. Primarily used to decide
           whether `uname -r` is likely to indicate something useful
           about the C implementation under test."""
        if self._is_cross_compiler is None:
            self._is_cross_compiler = self.probe_cross_compiler()
        return self._is_cross_compiler

    def probe_cross_compiler(self):
        """Detect whether this is a cross compiler.  Logic borrowed
           from autoconf 2.61's _AC_COMPILER_EXEEXT_CROSS.  Note in
           particular that (according to the comments in that code)
           attempting to compile and execute a no-op program is
           insufficient."""

        test_c = None
        try:
            test_c = named_tmpfile(prefix="cci", suffix="c")
            f = open(test_c, "w")
            f.write("""\
#include <stdio.h>
int main(void)
{
  FILE *f = tmpfile();
  fputs("blort", f);
  return ferror(f) || fclose(f) != 0;
}
""")
            f.close()
            self.log.progress_tick()
            self.log.log("attempting to create an executable:",
                         universal_readlines(test_c))
            # We gonna just assume invoking the compiler without any
            # options produces an executable named 'a.out', at least till
            # I get back to my Windows VM.
            (rc, msg) = self.log.invoke(self.base_cmd + [test_c])
            if rc != 0:
                self.log.fatal("failed to create a test executable")
            self.log.progress_tick()
            self.log.log("running said executable")
            (rc, msg) = self.log.invoke(["./a.out"])
        finally:
            delete_if_exists("a.out")
            if test_c is not None: delete_if_exists(test_c)

        if rc != 0:
            self.log.log("execution failed, assuming a cross compiler")
            return 1
        else:
            self.log.log("execution succeeded, assuming a native compiler")
            return 0

    def test_invoke_basic(self, code, action, outname, opts,
                          suppress_progress_tick=0, want_output=0):
        """Invoke the compiler on CODE to do ACTION and produce OUTNAME,
           providing additional options OPTIONS.  Return the exit code
           and the error messages, after cleaning up temporary files.
           If WANT_OUTPUT is true, the output is appended to the error
           messages.  If SUPPRESS_PROGRESS_TICK is true, does not call
           progress_tick() (see above)."""

        test_c = None
        test_s = None
        try:
            test_c = named_tmpfile(prefix="cct", suffix="c")
            test_s = subst_filename(test_c, outname)

            cmd = self.base_cmd[:]
            cmd.extend(opts)
            cmd.extend(subst_filename(test_c, action))
            cmd.append(test_c)

            f = open(test_c, "w")
            f.write(code)
            f.write("\n")
            f.close()

            if not suppress_progress_tick:
                self.log.progress_tick()
            self.log.log("compiling:", code.split("\n"))
            (rc, output) = self.log.invoke(cmd)
            if rc == 0 and want_output:
                try:
                    output.extend(universal_readlines(test_s))
                except EnvironmentError, e:
                    # Filter out ENOENT; under some circumstances the
                    # desired output goes to stdout instead of the file.
                    if e.errno != errno.ENOENT: raise
            return (rc, output)

        finally:
            delete_if_exists(test_c)
            delete_if_exists(test_s)

    def test_invoke(self, code, action, outname,
                    mode, opts=None, defines=None,
                    suppress_progress_tick=0, want_output=0):
        """Invoke the compiler on CODE, in the compilation mode indicated
           by ACTION, MODE, and OPTS, defining preprocessor
           macros as given by DEFINES.  Return the exit code and the
           error messages, after cleaning up temporary files."""

        xopts = []
        if mode.conform:
            xopts.extend(self.clevel_opts_std)
        else:
            xopts.extend(self.clevel_opts_ext)
        if mode.thread:
            xopts.extend(self.thread_opt)
        if opts is not None:
            xopts.extend(opts)
        if defines is not None:
            for d in defines:
                cmd.append(self.define_opt + d)

        return self.test_invoke_basic(code, action, outname, xopts,
                                      suppress_progress_tick, want_output)

    def test_compile(self, code, mode, opts=[], defines=[]):
        """Convenience function for requesting compilation at least up to
           and including semantic validation."""
        return self.test_invoke(code,
                                self.compile_cmd,
                                self.compile_out,
                                mode, opts, defines)

    def test_preproc(self, code, mode, opts=[], defines=[],
                     want_output=0):
        """Convenience function for requesting preprocessing only."""
        return self.test_invoke(code,
                                self.preproc_cmd,
                                self.preproc_out,
                                mode, opts, defines,
                                want_output=want_output)

class Metadata:
    """Records all the metadata associated with an inventory.
       Responsible for identifying the C compiler and runtime,
       and selecting an appropriate set of compilation modes."""

    def __init__(self, cfg, log):
        self.cfg   = cfg
        self.log   = log
        self.cc    = None
        self.modes = []

    def probe_compiler(self, cmd, ccenv={}):
        """Identify the compiler that is invoked by CMD (with environment
           settings CCENV) and instantiate an appropriate Compiler object."""

        def parse_output(msg, compilers):
            # This is a nested routine so we can use "return" to break
            # out of two loops at once.
            for line in msg:
                if line.find("error") != -1:
                    for (imitated, macro, name) in compilers:
                        if re.search(r'\b' + name + r'\b', line):
                            return name
                    if re.search(r'\bUNKNOWN\b', line):
                        return "UNKNOWN"
            return "FAIL"

        self.log.begin_test("identifying compiler")

        for k, v in ccenv.items():
            os.environ[k] = v

        # Construct a source file that will fail to compile with
        # exactly one #error directive, identifying the compiler in
        # use.  We do it this way because at this point we have no
        # control over compilation mode or output; an #error will
        # reliably produce an error message that invoke() knows how
        # to capture, and no output file.

        # Some compilers are imitated - their identifying macros are
        # also defined by other compilers.  Sort these to the end.
        compilers = [(cc.imitated, cc.id_macro, name)
                     for (name, cc) in self.cfg.compilers.items()]
        compilers.sort()

        test1 = None
        test2 = None
        test2_o = None
        try:
            test1 = named_tmpfile(prefix="cci", suffix="c")
            f = open(test1, "w")
            f.write("#if 0\n")
            for (imitated, macro, name) in compilers:
                f.write("#elif defined %s\n#error %s\n" % (macro, name))
            f.write("#else\n#error UNKNOWN\n#endif\n")
            f.close()

            self.log.progress_tick()
            self.log.log("probing compiler identity:",
                         universal_readlines(test1))
            (rc, msg) = self.log.invoke(cmd + [test1])
            compiler = parse_output(msg, compilers)

            if compiler == "FAIL":
                self.log.fatal("unable to parse compiler output.")
            if compiler == "UNKNOWN":
                self.log.fatal("no configuration available for this "
                               "compiler.  Please add appropriate "
                               "settings to " +
                               repr(self.cfg.compiler_cfg_fname) + ".")

            # Confirm the identification.
            cc = self.cfg.compilers[compiler]
            version_argv = cc.version.split()
            version_out = cc.version_out

            for arg in version_argv:
                if arg.startswith("$."):
                    test2 = named_tmpfile(prefix="cci", suffix=arg[2:])
                    f = open(test2, "w")
                    f.write("int dummy;\n")
                    f.close()
                    test2_o  = subst_filename(test2, version_out)
                    version_argv = subst_filename(test2, version_argv)
                    break

            self.log.progress_tick()
            (rc, msg) = self.log.invoke(cmd + version_argv)
            if rc != 0:
                self.log.fatal("detailed version request failed")
            mm = "\n".join(msg[1:]) # throw away the command line
            version_re = re.compile(cc.id_regexp, re.VERBOSE|re.DOTALL)
            match = version_re.search(mm)
            if not match:
                self.log.fatal("version information not as expected: "
                               "is this really " + compiler + "?")

            try:
                version = match.group("version")
            except IndexError:
                versio1 = match.group("version1")
                versio2 = match.group("version2")
                if group_matched(versio1): version = versio1
                elif group_matched(versio2): version = versio2
                else:
                    self.log.fatal("version number not found")

            details = -1
            try:
                details = match.group("details")
            except IndexError:
                try:
                    detail1 = match.group("details1")
                    if group_matched(detail1) and detail1.lower() != compiler:
                        details = detail1
                    else:
                        detail2 = match.group("details2")
                        if group_matched(detail2) and \
                                detail2.lower() != compiler:
                            details = detail2
                except IndexError:
                    pass

            if details != -1:
                ident = "%s %s (%s)" % (compiler, version, details)
            else:
                ident = "%s %s" % (compiler, version)

        finally:
            if test1   is not None: delete_if_exists(test1)
            if test2   is not None: delete_if_exists(test2)
            if test2_o is not None: delete_if_exists(test2_o)

        self.log.end_test(ident)

        self.compiler = compiler
        self.compiler_label = ident
        self.cc = Compiler(cmd, cc, self.log)
        self.select_c_standard(self.cc, cc)
        return self.cc

    def probe_runtime(self):

        # Probing the runtime uses the same technique as above, because
        # it's convenient.

        def parse_output(msg, rtnames):
            # This is a nested routine so we can use "return" to break
            # out of two loops at once.
            for line in msg:
                if line.find("error") != -1:
                    for name in rtnames:
                        if re.search(r'\b' + name + r'\b', line):
                            return name
                    if re.search(r'\bUNKNOWN\b', line):
                        return "UNKNOWN"
            return "FAIL"

        self.log.begin_test("identifying C runtime")
        idcode = ["#include <errno.h>", "#if 0"]
        for (name, rtspec) in self.cfg.runtimes.items():
            idcode.append("#elif " + rtspec.id_expr)
            idcode.append("#error " + name)
        idcode.extend(("#else", "#error UNKNOWN", "#endif"))

        (rc, msg) = self.cc.test_preproc("\n".join(idcode),
                                         CompilationMode())
        runtime = parse_output(msg, self.cfg.runtimes.keys())
        if runtime == "FAIL":
            self.log.fatal("unable to parse compiler output.")
        if runtime == "UNKNOWN":
            self.log.error("no configuration available for this C runtime.  "
                           "Please add appropriate settings to " +
                           repr(self.cfg.runtimes_cfg_fname) + ".")
            self.dump_potential_system_id_macros()
            raise SystemExit(1)

        rtspec = self.cfg.runtimes[runtime]

        if rtspec.version_detector is None:
            if cc.is_cross_compiler():
                self.log.fatal("Cross compiling to target that does not reveal "
                               "version of C runtime to preprocessor.")

            # If we are not cross compiling, we can probably trust
            # os.uname()[2] == `uname -r` to tell us a useful number.
            version = os.uname()[2]

        else:
            (rc, out) = self.cc.test_preproc("#include <errno.h>\n" +
                                             rtspec.version_detector,
                                             CompilationMode(),
                                             want_output=1)
            if rc != 0:
                self.log.fatal("failed to probe C runtime version")
            squishre = re.compile("[ \t\r\n\v\f\"\']+")
            for line in out:
                line = squishre.sub("", line)
                if line[:8] == "VERSION=":
                    version = line[8:]
                    break
            else:
                self.log.fatal("failed to parse version detector output")

        if rtspec.version_adjust is not None:
            d = {}
            exec re.sub("(?m)^\s*\|", "", rtspec.version_adjust) \
                in globals(), d
            version = d["version_adjust"](version)

        self.runtime_id = runtime
        self.runtime_version = version
        self.log.end_test("%s %s" % (rtspec.label, version))

    def select_c_standard(self, cc, cspec):
        """Determine the most recent level of the C standard supported by
           this compiler, and enable it."""

        levels = [
            ("2011", cspec.c2011, ["201112L"]),
            ("1999", cspec.c1999, ["199901L"]),
            # There are two possible values of __STDC_VERSION__ for C1989.
            ("1989", cspec.c1989, ["199401L", "1"])
        ]
        self.log.begin_test("determining ISO C conformance level")
        for level, probe_opts, version_values in levels:
            if probe_opts == "no":
                continue

            if probe_opts == "":
                opts_ext = []
                opts_std = []
            else:
                x = probe_opts.find('|')
                if x == -1:
                    opts_ext = probe_opts.split()
                    opts_std = opts_ext[:]
                else:
                    opts_ext = probe_opts[:x].split()
                    opts_std = probe_opts[(x+1):].split()

            if cspec.conform != "":
                opts_std.extend(conform.split())

            self.log.log("trying C%s %s" % (level, repr(opts_std)))
            code = "#if 1 "
            for val in version_values:
                code = code + " && __STDC_VERSION__ != " + val
                code = code + "\n#error \"wrong version\"\n#endif\n"

            (rc, msg) = cc.test_invoke_basic(code,
                                             cc.preproc_cmd,
                                             cc.preproc_out,
                                             opts_std)
            if rc == 0:
                self.log.end_test("C"+level)
                cc.clevel_opts_std = opts_std
                cc.clevel_opts_ext = opts_ext
                return

        self.log.end_test("failed")
        self.log.fatal("failed to determine ISO C conformance level. "
                       "Check configuration for %s in %s."
                       % (self.compiler, self.cfg.compiler_cfg_fname))



    def smoke_test(self):
        """Perform tests which, if they fail, indicate something horribly
           wrong with the compiler and/or our usage of it (so there is no
           point in continuing with the test run).  Either returns
           successfully, or issues a fatal error."""

        self.log.begin_test("smoke test")

        test_modes = [
            (self.cc.test_preproc, 0, "preprocess"),
            (self.cc.test_preproc, 1, "preprocess (conformance mode)"),
            (self.cc.test_compile, 0, "compile"),
            (self.cc.test_compile, 1, "compile (conformance mode)")
        ]

        # This code should compile without complaint.
        for (action, conform, tag) in test_modes:
            self.log.log("smoke test: %s, should succeed" % tag)
            (rc, msg) = action("#include <stdarg.h>\nint dummy;",
                               CompilationMode(conform))
            if rc != 0:
                self.log.fatal("failed to %s simple test program. "
                               "Check configuration for %s in %s."
                               % (tag, self.compiler,
                                  self.cfg.compiler_cfg_fname))

        # This code should _not_ compile, in any mode, nor should it
        # preprocess.
        for (action, conform, tag) in test_modes:
            self.log.log("smoke test: %s, should fail due to nonexistence"
                         % tag)
            (rc, msg) = action("#include <nonexistent.h>\nint dummy;",
                               CompilationMode(conform))
            if rc == 0 or not self.cc.failure_due_to_nonexistence(
                    msg, "nonexistent.h"):
                self.log.fatal(
                    "failed to detect nonexistence of <nonexistent.h>"
                    " (%s). Check configuration for %s in %s."
                    % (tag, self.compiler, self.cfg.compiler_cfg_fname))

        # We should be able to tell that the error in this code is on line 3.
        for conform in (0,1):
            self.log.log("smoke test: error on specific line (conform=%d)"
                     % conform)
            (rc, msg) = self.cc.test_compile("int main(void)\n"
                                             "{\n"
                                             "  not_a_type v;\n"
                                             "  return 0;\n"
                                             "}",
                                             CompilationMode(conform));
            # The source file will be the last space-separated token on
            # the first line of 'msg'.
            srcf = msg[0].split()[-1]

            for line in msg:
                m = self.cc.errloc_re.search(line)
                if m and m.group("file") == srcf:
                    if int(m.group("line")) == 3:
                        break
                    else:
                        self.log.fatal("error on unexpected line %s. "
                                       "Check configuration for %s in %s."
                                       % (m.group(line), self.compiler,
                                          self.cfg.compiler_cfg_fname))
            else:
                self.log.fatal("failed to detect error on line 3. "
                               "Check configuration for %s in %s."
                               % (self.compiler, ccs_f,
                                  self.cfg.compiler_cfg_fname))

        self.log.end_test("ok")

    def dump_potential_system_id_macros(self):
        macro_name_extractor = re.compile(
            r"^#define\s+([A-Za-z_][A-Za-z0-9_]*)\b")
        not_system_id_macros = re.compile(self.cfg.not_system_id_macros,
                                          re.VERBOSE)
        # we use errno.h for this because it's universal, reasonably likely
        # to expose library-identification macros, and doesn't have a ton of
        # other junk in it.
        (rc, output) = self.test_invoke_basic("#include <errno.h>",
                                              self.preproc_cmd,
                                              self.preproc_out,
                                              self.dump_macros,
                                              suppress_progress_tick=1,
                                              want_output=1)
        if rc != 0:
            self.log.fatal("failed to dump predefined macros")

        macros = []
        for line in output:
            m = macro_name_extractor.match(line)
            if m:
                name = m.group(1)
                if not not_system_id_macros.match(name):
                    macros.append(name)
        macros.sort()
        sys.stderr.write("Potential system-identifying macros:\n")
        for m in macros:
            sys.stderr.write("  %s\n" % m)

    def report(self, outf):
        """Report the identity of the compiler and how we're going to
           use it."""
        outf.write("compilation options: %s\n" % " ".join(self.cc.compile_cmd))
        outf.write("standard mode: %s\n" % " ".join(self.cc.clevel_opts_std))
        outf.write("extended mode: %s\n" % " ".join(self.cc.clevel_opts_ext))

#
# Headers and high-level analysis
#

class KnownError:
    """A known way in which a header (or headers) can fail to compile
       successfully.  NAME is a mnemonic label for this failure case;
       HEADERS are the headers it applies to ("*" for potentially all of
       them); REGEXP is a regular expression that will match error messages
       indicating this failure mode; DESC is a human-readable description
       of the problem; and CAUTION is true if this problem is not so severe
       that the header can't be used at all.  These correspond precisely to
       the fields of each stanza of config/errors.ini."""
    def __init__(self, name, headers, regexp, desc, caution):
        self.name = name
        self.headers = headers
        self.regexp = re.compile(regexp, re.VERBOSE)
        self.desc = desc
        self.caution = caution

    def search(self, msg):
        """True if the error message MSG indicates this known error."""
        return self.regexp.search(msg)

# Stopgap value used to preserve data structure consistency when we
# hit a failure mode that isn't coded into config/errors.ini yet.
UnrecognizedError = KnownError("<unrecognized>", "*", "", "", 0)

class ContentTestResultCluster:
    """Data structure object used by ContentTestResult."""
    def __init__(self, std, mod, stype, symbols):
        self.stype = stype
        if mod == "":
            self.category = std
        else:
            self.category = std + ":" + mod
        self.symbols = symbols
        self.symbols.sort()

    def __str__(self):
        if not self.symbols:
            return "%s:%s:" % (self.stype, self.category)
        else:
            return "%s:%s: %s" % (self.stype, self.category,
                                  " ".join(self.symbols))

class ContentTestResult:
    """Results of a test for contents.  Instantiate from a TestProgram
       instance; walks the data structure and computes the appropriate
       set of annotations."""

    def __init__(self, tester, cfg):
        self.missing_items = []
        self.wrong_items = []
        self.uncertain_items = []

        self.badness = 0

        CTRC = ContentTestResultCluster

        for std, mods in tester.std_index.items():
            for mod, components in mods.items():
                for comp in components:

                    missing = {}
                    wrong = {}
                    uncertain = {}
                    all_symbols = {}

                    for item in comp.items:
                        all_symbols[item.tag] = 1

                    disabled = comp.disabled_items()

                    for item in disabled:
                        if item.meaning == TestItem.INCORRECT:
                            wrong[item.tag] = 1
                        elif item.meaning == TestItem.MISSING:
                            missing[item.tag] = 1
                        else:
                            assert item.meaning == TestItem.AMBIGUOUS
                            uncertain[item.tag] = 1

                    # A 'missing' item trumps a 'wrong' or 'uncertain' item
                    # with the same tag.
                    for tag in missing.keys():
                        if wrong.has_key(tag): del wrong[tag]
                        if uncertain.has_key(tag): del uncertain[tag]

                    if (std == tester.baseline and
                        (missing or wrong or uncertain) and
                        cfg.required_modules.has_key(mod)):
                        self.badness = 1

                    if (len(missing) + len(wrong) + len(uncertain)
                        == len(all_symbols)):
                        # All the symbols in this module are busted
                        # somehow.  Treat "uncertain" as collectively
                        # trumping "wrong" and "missing", and
                        # "missing" as collectively trumping "wrong",
                        # for compactness' sake.
                        cluster = CTRC(std, mod, comp.label, [])
                        if uncertain:
                            self.uncertain_items.append(cluster)
                        elif missing:
                            self.missing_items.append(cluster)
                        else:
                            assert wrong
                            self.wrong_items.append(cluster)
                    else:
                        if missing:
                            self.missing_items.append(
                                CTRC(std, mod, comp.label, missing.keys()))
                        if wrong:
                            self.wrong_items.append(
                                CTRC(std, mod, comp.label, wrong.keys()))
                        if uncertain:
                            self.uncertain_items.append(
                                CTRC(std, mod, comp.label, uncertain.keys()))

        if tester.all_disabled():
            self.badness = 2

    def output(self, outf):
        for cluster in self.missing_items:
            outf.write("  $M %s\n" % cluster)
        for cluster in self.wrong_items:
            outf.write("  $W %s\n" % cluster)
        for cluster in self.uncertain_items:
            outf.write("  $X %s\n" % cluster)

class Dependency:
    """Either a header, or a [special] dependency from config/prereqs.ini.
       These are treated interchangeably in some contexts.  Dependency
       objects are usable as dictionary keys."""

    # A dependency may or may not be "present" on a given system.
    UNKNOWN = '?'
    ABSENT  = '-'
    PRESENT = ' '

    def __init__(self, name):
        self.what = self.__class__.__name__
        self.name = name

        # These are here only for interchangeability's sake.
        self.presence = self.UNKNOWN
        self.deplist = []

    def __hash__(self):
        return hash(self.what) ^ hash(self.name)

    def __cmp__(self, other):
        return cmp(self.what, other.what) or cmp(self.name, other.name)

    def __str__(self):
        return self.name

    def with_dependencies(self, already=None):
        """Return a list containing all of this dependency's own
           dependencies (in the appropriate order) and then the
           dependency itself.  Duplicates are filtered out."""

        assert self.presence != self.UNKNOWN
        # Buggy headers may still be dependencies!  (actually happens
        # e.g. when <rpc/rpc.h> suffers from 'legacy_type_decls')
        if self.presence == self.ABSENT:
            return []

        if already is None:
            already = {}
        else:
            if already.has_key(self):
                return []

        already[self] = 1

        rv = []
        for dep in self.deplist:
            rv.extend(dep.with_dependencies(already))
        rv.append(self)
        return rv

    def test(self, cc, log):
        """Test whether this dependency is present and usable; set
           self.presence accordingly.  Subclasses may need to override
           this method."""
        self.presence = self.PRESENT

    def generate(self, out):
        """Append code for this dependency to OUT (which is a list of strings).
           Only append code for this dependency itself; not for its transitive
           dependencies (if any).  Subclasses must override this method."""
        raise NotImplementedError

class SpecialDependency(Dependency):
    """Used to represent [special] dependencies from config/prereqs.ini.
       Stubs some Header methods and properties so it can be treated
       like one when convenient."""

    def __init__(self, header, text):
        Dependency.__init__(self, header)
        self.text = text.strip().split("\n")

    def __str__(self):
        return "[S:%s]" % self.name

    def generate(self, out):
        out.extend(self.text)

class Header(Dependency):
    """A Header instance represents everything that is currently known
       about a single header file, and knows how to carry out a sequence
       of tests of the header:

         - whether it exists at all
         - whether it can be compiled successfully, in isolation
         - if it can't be compiled successfully in isolation,
           whether this can be fixed by including other headers first
         - for some headers, whether its contents are as expected

       Information about other headers to try including first is stored
       in the configuration file 'config/prereqs.ini', q.v."""

    # State codes as written to the file.  Some of these are also used
    # for internal flags.  UNKNOWN, ABSENT, and PRESENT must match the
    # definitions in Dependency; they are redefined here because of
    # Python's scoping rules.
    UNKNOWN    = '?'
    ABSENT     = '-'
    BUGGY      = '!'

    PRESENT    = ' '
    INCOMPLETE = '*'
    CORRECT    = '+'

    PRES_DEP   = '%'
    INCO_DEP   = '&'
    CORR_DEP   = '@'

    PRES_CAU   = '~'
    INCO_CAU   = '^'
    CORR_CAU   = '='

    # Complete list of valid state codes, for validation on reread.
    STATES = (UNKNOWN,  ABSENT,     BUGGY,
              PRESENT,  INCOMPLETE, CORRECT,
              PRES_DEP, INCO_DEP,   CORR_DEP,
              PRES_CAU, INCO_CAU,   CORR_CAU)

    # Human readable labels for the states.
    STATE_LABELS = {
        UNKNOWN    : "UNKNOWN",
        ABSENT     : "ABSENT",
        BUGGY      : "BUGGY",
        PRESENT    : "PRESENT",
        INCOMPLETE : "INCOMPLETE",
        CORRECT    : "CORRECT",
        PRES_DEP   : "PRESENT (DEPENDENT)",
        INCO_DEP   : "INCOMPLETE (DEPENDENT)",
        CORR_DEP   : "CORRECT (DEPENDENT)",
        PRES_CAU   : "PRESENT (CAUTION)",
        INCO_CAU   : "INCOMPLETE (CAUTION)",
        CORR_CAU   : "CORRECT (CAUTION)",
    }

    def __init__(self, name, cfg, dataset):
        Dependency.__init__(self, name)

        self.cfg     = cfg
        self.dataset = dataset

        # done in Dependency.__init__, preserved here for documentation:
        #self.presence  = self.UNKNOWN # can be ABSENT, BUGGY, PRESENT

        self.contents  = self.UNKNOWN # can be PRESENT, INCOMPLETE, CORRECT
        self.depends   = None # None=unknown, 0=no, 1=yes
        self.conflict  = None # None=unknown, 0=no, 1=yes
        self.caution   = 0    # 0=no or unknown, 1=yes, 2=contents only

        # done in Dependency.__init__, preserved here for documentation:
        #self.deplist = []
        self.conflist = []
        self.errlist = []

        self.content_results = None

    def log_tests(self, log):
        outf = StringIO.StringIO()
        outf.write(" presence: " + self.STATE_LABELS[self.presence] + "\n")
        outf.write(" contents: " + self.STATE_LABELS[self.contents] + "\n")
        outf.write("  depends: " + repr(self.depends) + "\n")
        outf.write("  caution: " + repr(self.caution) + "\n")
        outf.write("  deplist: %s\n"
                   % " ".join([h.name for h in self.deplist]))
        outf.write("  errlist: %s\n"
                   % " ".join([h.name for h in self.errlist]))

        if self.content_results is not None:
            outf.write(" contents:\n")
            self.content_results.output(outf)

        log.log("%s = %s" % (self.name, self.state_label()),
                outf.getvalue().split("\n"))

    def log_conflicts(self, log):
        log.log("%s = %s" % (self.name, self.state_label()),
                [" conflict: " + repr(self.conflict),
                 " conflist: " + " ".join([h.name for h in self.conflist])])

    def state_code(self):
        if self.presence != self.PRESENT:
            # unknown/absent/buggy exclude all other indicators.
            return self.presence
        else:
            assert self.depends is not None

            caution = (self.conflict or self.caution)
            if self.contents == self.PRESENT:
                if        caution: return self.PRES_CAU
                elif self.depends: return self.PRES_DEP
                else:              return self.PRESENT
            elif self.contents == self.INCOMPLETE:
                if        caution: return self.INCO_CAU
                elif self.depends: return self.INCO_DEP
                else:              return self.INCOMPLETE
            else:
                assert self.contents == self.CORRECT
                if        caution: return self.CORR_CAU
                elif self.depends: return self.CORR_DEP
                else:              return self.CORRECT

    def state_label(self):
        return self.STATE_LABELS[self.state_code()]

    def output(self, outf):
        outf.write("%s%s\n" % (self.state_code(), self.name))
        if len(self.deplist) == 0:
            pass
        elif isinstance(self.deplist[0], SpecialDependency):
            assert len(self.deplist) == 1
            outf.write("  $S %s\n" % self.deplist[0].name)
        else:
            self.output_annlist(outf, 'P', self.deplist)
        self.output_annlist(outf, 'C', self.conflist)
        self.output_annlist(outf, 'E', self.errlist)
        if self.content_results is not None:
            self.content_results.output(outf)

    def output_annlist(self, outf, tag, lst):
        if lst:
            outf.write("  $%s %s\n" %
                       (tag, " ".join([h.name for h in lst])))

    def extend_errlist(self, errs):
        for e in errs:
            for x in self.errlist:
                if x.name == e.name:
                    break
            else:
                self.errlist.append(e)
                if e.caution:
                    self.caution = 1
                else:
                    self.presence = self.BUGGY

    def record_errors(self, log, msg, ignore_unknown=0):
        errs = self.cfg.is_known_error(msg, self.name)
        if errs is not None:
            log.progress_note("*** errors detected: %s"
                              % " ".join([err.name for err in errs]))
            self.extend_errlist(errs)
        else:
            if ignore_unknown: return

            log.error("unrecognized failure mode for <%s>. "
                      "Please investigate and add an entry to %s."
                      % (self.name, self.cfg.errors_fname))
            self.extend_errlist([UnrecognizedError])

    def record_conflict(self, other):
        self.conflict = 1
        for hh in self.conflist:
            if hh is other:
                break
        else:
            self.conflist.append(other)

    def generate(self, out):
        out.append("#include <%s>" % self.name)

    def test(self, cc, log):
        """Perform all checks on this header in isolation (up to
           dependencies).  This blindly calls itself on other header
           objects, and so must be idempotent.

           Conflict checking is done in a second pass, by the dataset."""

        if self.presence != self.UNKNOWN: return

        # Test dependencies first so the logs are not jumbled.
        for h in self.dataset.deps.get(self, []):
            h.test(cc, log)

        log.begin_test(self.name + " " + str(self.dataset.mode))

        self.test_presence(cc, log)
        self.test_depends(cc, log)
        self.test_contents(cc, log)
        self.log_tests(log)

        log.end_test(self.state_label().lower())

    def test_presence(self, cc, log):
        if self.presence != self.UNKNOWN: return

        log.log("testing presence of %s" % self.name)
        (rc, msg) = cc.test_preproc("#include <%s>" % self.name,
                                    self.dataset.mode)
        if rc != 0 and cc.failure_due_to_nonexistence(msg, self.name):
            self.presence = self.ABSENT
        else:
            # Ignore failures which are not due to nonexistence at this
            # point.  Some systems (e.g. IRIX6) have headers that require
            # their dependencies in order to _preprocess_ correctly.
            self.presence = self.PRESENT

    def test_depends(self, cc, log):
        if self.depends is not None: return
        if self.presence != self.PRESENT: return

        possible_deps = []
        for h in self.dataset.deps.get(self, []):
            assert h.presence != h.UNKNOWN
            # Buggy headers may still be dependencies!  (actually happens
            # e.g. when <rpc/rpc.h> suffers from 'legacy_type_decls')
            if h.presence != h.ABSENT:
                possible_deps.append(h)

        log.log("dependency test %s mode %s possibilities: [%s]" %
               (self.name, self.dataset.mode,
                " ".join([h.name for h in possible_deps])))

        failures = []

        # dependency_combs is guaranteed to produce an empty set as the first
        # item in its returned list, and the complete set as the last item.
        for candidate_set in dependency_combs(possible_deps):
            log.log("dependency test %s mode %s candidates: [%s]" %
                   (self.name,
                    self.dataset.mode,
                    " ".join([h.name for h in candidate_set])))

            includes = []
            already = {}
            for h in candidate_set:
                for hh in h.with_dependencies(already):
                    hh.generate(includes)

            # As a sanity check, confirm that this header can be
            # included twice in a row.  Failures of this check are
            # rare and handled via config/errors.ini.
            self.generate(includes)

            # If the headers under test contain nothing but macros,
            # we could trip over the requirement that a translation unit
            # contain at least one top-level definition or declaration
            # (C99 6.9 -- implicit in the grammar; the "translation-unit"
            # production does not accept an empty token sequence).
            includes.append("int avoid_empty_translation_unit;")

            (rc, msg) = cc.test_compile("\n".join(includes),
                                        self.dataset.mode)
            if rc == 0:
                self.deplist = candidate_set
                self.depends = len(self.deplist) > 0
                return

            if len(failures) > 0: failures.append("")
            failures.extend(msg)

        # If we get here, there is a serious problem.
        # Look for a known bug in the last set of messages, which will be
        # the maximal dependency set and therefore the least likely to have
        # problems.
        self.record_errors(log, msg)
        self.presence = self.BUGGY

    def test_contents(self, cc, log):
        if self.presence != self.PRESENT: return
        if self.contents != self.UNKNOWN: return

        if not self.cfg.content_tests.has_key(self.name):
            log.log("no contents test available for %s" % self.name)
            self.contents = self.PRESENT
            return

        tester = self.cfg.content_tests[self.name]

        log.log("contents test for %s in mode %s" %
               (self.name, self.dataset.mode))

        buf = []
        for item in self.with_dependencies():
            item.generate(buf)
        buf.append("")
        tester.generate(buf)
        (rc, base_msg) = cc.test_compile("\n".join(buf),
                                         self.dataset.mode)
        if rc == 0:
            self.contents = self.CORRECT
            return

        msg = base_msg
        prev_disabled_tags = []
        while rc != 0:
            if tester.all_disabled():
                # Everything being disabled at the top of the loop means that
                # we tried to compile a source file with everything disabled
                # and it _still_ didn't go through.
                log.error("unrecognized failure mode for <%s> (contents tests)."
                         % self.name)
                self.extend_errlist(0, 0, [UnrecognizedError])
                return

            # Record any known errors (for instance, a macro might
            # trigger the infamous legacy_type_decls).  Do not record
            # unknown errors; they are probably from the test code,
            # not the header.
            self.record_errors(log, msg, ignore_unknown=1)

            # The source file will be the last space-separated token on
            # the first line of 'msg'.
            srcf = msg[0].split()[-1]

            for line in msg:
                m = cc.errloc_re.search(line)
                if m and m.group("file") == srcf:
                    # The test program is constructed to ensure that
                    # each thing-under-test occupies exactly one line, so
                    # we don't need to understand the error message beyond
                    # which line it's on.
                    tag = tester.disable_line(int(m.group("line")), log)
                    if tag:
                        log.log("disabled %s" % tag)

            disabled_tags = tester.disabled_tags()
            if disabled_tags == prev_disabled_tags:
                # Nothing changed, so the compiler is complaining about
                # something we don't know how to turn off.
                log.error("unrecognized failure mode for <%s> (contents tests)."
                          % self.name)
                break
            prev_disabled_tags = disabled_tags

            buf = []
            for item in self.with_dependencies():
                item.generate(buf)
            buf.append("")
            tester.generate(buf)
            log.log("retry contents test for %s (mode %s)" %
                    (self.name, self.dataset.mode))
            (rc, msg) = cc.test_compile("\n".join(buf),
                                        self.dataset.mode)

        # If we get here, we just had a successful compilation with at
        # least some items disabled.  Annotate accordingly.
        result = tester.results(self.cfg)
        if result.badness == 0:
            # Only optional items failed the tests.
            self.contents = self.INCOMPLETE
        elif result.badness == 1:
            # Some required items failed the tests.
            self.contents = self.INCOMPLETE
            self.caution = 2 # contents-only caution (doesn't inhibit
                             # conflict tests)
        else:
            # _All_ items failed the tests.
            assert result.badness == 2
            self.presence = self.BUGGY

        self.content_results = result

class ConflictMatrix:
    """Data structure used by the conflict tester.  Provides a canonical
       ordering of the headers, and records which pairs have already been
       tested against each other in matrix format:

           A B C .. Z
         A 1 0 0    0
         B 0 1 0    0
         C 0 0 1    0
         :
         Z 0 0 0    1

       bit [X][Y] is 1 if #include <X.h> followed by #include <Y.h>
       provokes no error, 2 if it does provoke an error, and 0 if this
       pair has not yet been tested.  Note that [X][Y]==1 *does not*
       imply [Y][X]==1; there are real systems where a conflict
       between X and Y only provokes an error in one of the two
       possible orderings.  However, [X][Y]==2 *does* imply [Y][X]==2,
       and we will go back and correct 1 to 2 if appropriate.

       The initial state of this matrix has 1s on the main diagonal
       and 0 everywhere else, because conflicts with self (can't
       include the same header twice) have been dealt with already and
       we don't need to track them.  (They're vanishingly rare, anyway.)

       Much of the algorithmic complexity of the conflict tester is in
       the service of filling in huge blocks of this matrix with each
       successful compilation."""

    def __init__(self, dataset, headers, log):
        self.debug = 0
        self.log = log
        self.dataset = dataset
        self.matrix = {}
        self.rdeps = {}
        self.live_headers = {}
        self.all_headers = sorthdr(headers)
        for x in headers:
            self.live_headers[x] = 1
            self.matrix[x] = {}
            self.rdeps[x] = []
            for y in headers:
                self.matrix[x][y] = int(x is y)

        # Take note of dependencies.  This has to be done in a second
        # pass so the matrix is fully constructed.
        for x in headers:
            for y in x.with_dependencies():
                if y is x or not isinstance(y, Header): continue

                # It is impossible to include x before y, and it is
                # mandatory to include y before x.  Therefore there
                # is no point testing either way.  Do not mark the
                # impossible direction as a conflict, because that would
                # be an asymmetric 2 and the assertions below might get
                # confused.
                self.matrix[x][y] = 1
                self.matrix[y][x] = 1

                # Add x to the list of things that depend on y. If y
                # conflicts with z, all the headers that depend on y
                # will also be considered to conflict with z.  This is
                # necessary for correctness -- otherwise we can miss
                # certain asymmetric conflicts.
                self.rdeps[y].append(x)

    def log_matrix(self, msg):
        if not self.debug:
            self.log.log(msg)
            return
        # U+00A0 NO-BREAK SPACE, U+2592 MEDIUM SHADE, U+2588 FULL BLOCK
        codes = [ "\xc2\xa0", "\xe2\x96\x92", "\xe2\x96\x88" ]
        lines = []
        for x in self.all_headers:
            lines.append("".join([codes[self.matrix[x][y]]
                                  for y in self.all_headers]))
        self.log.log(msg, lines)

    def check_completely_done(self, cc):
        # Determine whether we are completely done with any headers.
        # If we are, remove them from the set of headers still of
        # interest (but not the conflict matrix).
        headers = self.live_headers.keys()
        for x in headers:
            for y in headers:
                if self.matrix[x][y] == 0 or self.matrix[y][x] == 0:
                    break
            else:
                self.log.log("conflict test: done with %s" % x)
                if x.conflict is None:
                    x.conflict = 0
                del self.live_headers[x]

    def record_conflict(self, cc, x, y):
        # We have identified a pairwise conflict; record it.
        self.record_conflict_1(cc, x, y)
        # Also record conflicts of all x's reverse dependencies with y,
        for xd in self.rdeps[x]:
            self.record_conflict_1(cc, xd, y)
        # and vice versa.
        for yd in self.rdeps[y]:
            self.record_conflict_1(cc, x, yd)

    def record_conflict_1(self, cc, x, y):
        self.matrix[x][y] = 2
        self.matrix[y][x] = 2
        self.log_matrix("conflict trial fail")

        x.record_conflict(y)
        y.record_conflict(x)
        self.log.progress_note("*** conflict identified: %s with %s" % (x, y))

    def record_ok(self, cc, tested):
        # For each header in the tested set, mark every header after
        # that header as ok after that header.
        for i in range(len(tested)):
            x = tested[i]
            if not isinstance(x, Header): continue
            for j in range(i+1, len(tested)):
                y = tested[j]
                if not isinstance(y, Header): continue

                if self.matrix[x][y] == 2 or self.matrix[y][x] == 2:
                    self.log.error("attempting to mark %s with %s as ok when "
                                   "already determined to conflict" % (x, y))
                else:
                    self.matrix[x][y] = 1
        self.log_matrix("conflict trial ok")

    def test_conflict_set(self, cc, cand):
        if self.debug:
            self.log.log("conflict candidate set: %s" % " ".join(cand))
        tset = []
        for i in range(len(cand)):
            # Pass specials through.
            if not isinstance(cand[i], Header):
                tset.append(cand[i])
                continue

            # If there is a known conflict of cand[i] with
            # cand[j] for any j < i, discard cand[i].
            for j in range(i):
                if not isinstance(cand[j], Header):
                    continue
                if self.matrix[cand[j]][cand[i]] == 2:
                    break
            else:
                tset.append(cand[i])
        if len(tset) < 2:
            return (1, tset)

        if self.debug:
            self.log.log("conflict trial set: %s" % " ".join(tset))

        eset = []
        already = {}
        for h in tset:
            if self.live_headers.has_key(h):
                eset.extend(h.with_dependencies(already))

        if self.debug:
            self.log.log("conflict extended set: %s" % " ".join(eset))

        # handling of specials
        includes = []
        for item in eset:
            item.generate(includes)

        # If the headers under test contain nothing but macros,
        # we could trip over the requirement that a translation unit
        # contain at least one top-level definition or declaration
        # (C99 6.9 -- implicit in the grammar; the "translation-unit"
        # production does not accept an empty token sequence).
        includes.append("int avoid_empty_translation_unit;")

        (rc, msg) = cc.test_compile("\n".join(includes),
                                    self.dataset.mode)
        return (rc == 0, eset)

    def find_single_conflict(self, cc, tset):
        # Binary search the end of the list for the earliest position
        # that has a conflict, filling in successes as we go.  Memoize
        # (lo, hi) pairs we've already tested so we don't repeat work.
        memo = { (0, len(tset)) : 0 }

        hi = floordiv(len(tset), 2)
        delta = hi
        prev_conflict = 1
        while 1:
            prev_delta = delta
            delta = max(1, floordiv(delta, 2))
            try:
                result = memo[(0, hi)]
            except KeyError:
                (result, tested) = self.test_conflict_set(cc, tset[:hi])
                memo[(0, hi)] = result
                if result:
                    self.record_ok(cc, tested)
                else:
                    self.log.log("conflict trial fail")
            if result:
                if prev_conflict and prev_delta == 1:
                    hi += 1
                    break

                hi += delta
                prev_conflict = 0
            else:
                if not prev_conflict and prev_delta == 1:
                    break

                hi -= delta
                prev_conflict = 1

        # Similarly, for the beginning of the list.  Note moving lo in the
        # opposite direction from hi on success or failure.
        lo = floordiv(hi, 2)
        delta = lo
        prev_conflict = 1
        while 1:
            prev_delta = delta
            delta = max(1, floordiv(delta, 2))
            try:
                result = memo[(lo, hi)]
            except KeyError:
                (result, tested) = self.test_conflict_set(cc, tset[lo:hi])
                memo[(lo, hi)] = result
                if result:
                    self.record_ok(cc, tested)
                else:
                    self.log.log("conflict trial fail")
            if result:
                if prev_conflict and prev_delta == 1:
                    lo -= 1
                    break

                lo -= delta
                prev_conflict = 0
            else:
                if not prev_conflict and prev_delta == 1:
                    break

                lo += delta
                prev_conflict = 1

        # The test set cannot be made any shorter without eliminating
        # the conflict.  We deduce that there is a conflict between
        # tset[lo] and tset[hi-1].  Verify this.
        (result, tested) = self.test_conflict_set(cc, [tset[lo], tset[hi-1]])
        if result:
            # This can legitimately happen if both tset[lo] and tset[hi-1]
            # conflict with something in the middle, but not with each other.
            # Record the absence of a pairwise conflict and proceed; the
            # logic below is equally sound if we did or didn't find the
            # conflict pair.
            self.record_ok(cc, [tset[lo], tset[hi-1]])
        else:
            self.record_conflict(cc, tset[lo], tset[hi-1])

        # Headers with one conflict are likely to have more.
        # Immediately retest tset[lo] and tset[hi-1] in first and last
        # position, with all headers we don't already know about in
        # that context.
        next_tests = []
        candidates = sorthdr(self.live_headers.keys())
        for x in tset[lo], tset[hi-1]:
            before = [x]
            after = []
            for y in candidates:
                if not self.matrix[x][y]: before.append(y)
                if not self.matrix[y][x]: after.append(y)
            after.append(x)
            next_tests.append(before)
            next_tests.append(after)

        return next_tests

    def find_conflicts(self, cc):
        # If there are no conflicts, testing all_headers in both
        # forward and reverse order will completely fill the matrix in
        # two compiler invocations.
        hh = self.all_headers[:]
        hh.reverse()
        queue = [ hh, self.all_headers ]

        # Make sure we don't repeat work (find_single_conflict can
        # generate the same "try this next" set repeatedly).
        already_tested = {}

        while 1:
            while len(queue) > 0:
                cand = queue.pop()

                if len(cand) == 1:
                    continue

                # find_single_conflict can also generate closely-related
                # test sets repeatedly.  Discard all headers which have
                # already been tested with both the head and the tail.
                if len(cand) > 2:
                    hd = cand[0]
                    tl = cand[-1]
                    ncand = [hd]
                    for c in cand[1:-1]:
                        if not (self.matrix[hd][c] and self.matrix[c][tl]):
                            ncand.append(c)
                    ncand.append(tl)
                    cand = ncand

                tag = tuple(cand)
                if not already_tested.has_key(tag):
                    already_tested[tag] = 1
                    (result, tested) = self.test_conflict_set(cc, cand)
                    if result:
                        self.record_ok(cc, tested)
                    else:
                        queue.extend(self.find_single_conflict(cc, tested))

            self.check_completely_done(cc)
            if len(self.live_headers) < 2:
                assert len(self.live_headers) == 0
                return # done

            # If we get here it is likely that only a few horizontal or
            # vertical stripes of the conflict matrix remain to be filled
            # in.  The most efficient way to do so is to find the header
            # with the most gaps remaining in its row/column and queue
            # it along with all of the gaps.  We need only consider the
            # headers that have not been removed from live_headers by
            # check_completely_done.

            headers = self.live_headers.keys()
            row_maxg = 0
            row_argmg = None
            col_maxg = 0
            col_argmg = None
            for x in headers:
                rowg = 0
                colg = 0
                for y in headers:
                    if not self.matrix[x][y]: colg += 1
                    if not self.matrix[y][x]: rowg += 1

                self.log.log("conflict test: %s: todo before %d after %d"
                             % (x, colg, rowg))
                if rowg > row_maxg:
                    row_maxg = rowg
                    row_argmg = x
                if colg > col_maxg:
                    col_maxg = colg
                    col_argmg = x

            # Only take the longest stripe, whichever dimension it's
            # in; toward the end of the process, we may have only
            # degenerate (length-1 / 2 headers) stripes in one
            # dimension, testing which is wholly redundant with
            # testing a long stripe in the other dimension.
            if row_maxg > col_maxg:
                assert row_argmg is not None
                row = []
                for x in headers:
                    if not self.matrix[x][row_argmg]: row.append(x)
                row.append(row_argmg)
                queue.append(row)

            if col_maxg >= row_maxg > 0:
                assert col_argmg is not None
                col = [col_argmg]
                for x in headers:
                    if not self.matrix[col_argmg][x]: col.append(x)
                queue.append(col)

class CompilerSpec:
    """Data carrier for compiler information, used by Configuration."""
    def __init__(self, cfg, sect, fname):
        for opt in cfg.options(sect):
            setattr(self, opt, cfg.get(sect, opt, raw=1).strip())

        for mopt in ["id_macro", "id_regexp", "define",
                     "compile", "preproc", "version",
                     "compile_out", "preproc_out", "version_out",
                     "conform", "c1989", "c1999", "c2011", "threads",
                     "notfound_re", "errloc_re"]:
            if not hasattr(self, mopt):
                raise RuntimeError("%s: incomplete configuration for %s "
                                   "(key '%s' missing)"
                                   % (fname, sect, mopt))

        if hasattr(self, 'imitated'):
            self.imitated = english_boolean(self.imitated)
        else:
            self.imitated = 0

class RtSpec:
    """Data carrier for C runtime information, used by Configuration."""
    def __init__(self, cfg, sect, fname):
        for opt in cfg.options(sect):
            setattr(self, opt, cfg.get(sect, opt, raw=1))

        for mopt in ["category", "label", "id_expr"]:
            if not hasattr(self, mopt):
                raise RuntimeError("%s: incomplate configuration for %s "
                                   "(key '%s' missing)"
                                   % (fname, sect, mopt))
        for oopt in ["version_detector", "version_adjust",
                     "max_features_macros"]:
            if not hasattr(self, oopt):
                setattr(self, oopt, None)

class Configuration:
    """All static configuration data (config/*.ini, content_tests/*.ini) is
       loaded into an instance of this class at startup."""

    def __init__(self, cfgdir, ctdir):
        self.cfgdir = cfgdir
        self.ctdir = ctdir
        self.load_compilers(os.path.join(cfgdir, "compilers.ini"))
        self.load_runtimes(os.path.join(cfgdir, "runtimes.ini"))
        self.load_known_errors(os.path.join(cfgdir, "errors.ini"))
        self.load_headers(os.path.join(cfgdir, "headers.ini"))
        self.load_deps(os.path.join(cfgdir, "prereqs.ini"))
        self.load_content_tests(ctdir)

    def load_compilers(self, fname):
        """Load information about known compilers.  This is left in a
           relatively 'uncooked' format because all but one of the compiler
           specifications will be unused on any given invocation; see
           Compiler.__init__ for how it will be processed."""
        self.compiler_cfg_fname = fname

        cfg = ConfigParser.ConfigParser()
        cfg.read(fname)

        self.compilers = {}
        for sect in cfg.sections():
            self.compilers[sect] = CompilerSpec(cfg, sect, fname)

    def load_runtimes(self, fname):
        self.runtimes_cfg_fname = fname

        cfg = ConfigParser.ConfigParser()
        cfg.read(fname)

        self.runtimes = {}
        for sect in cfg.sections():
            if sect != "META":
                self.runtimes[sect] = RtSpec(cfg, sect, fname)

        self.not_system_id_macros = cfg.get("META", "not_system_id_macros",
                                            raw=1)

    def load_headers(self, fname):
        """Load the complete set of headers to process.  We do not instantiate
           Header objects at this time, because each Dataset object (of which
           there are potentially several on any given run) needs its own set
           of them."""
        cfg = ConfigParser.ConfigParser()
        cfg.read(fname)

        # This program doesn't need to know the labels for each standard,
        # but it does need to know the sort order, since we can't count on
        # ConfigParser preserving file order.  Since we're looking anyway,
        # make sure every section has an entry in the [standards] block.
        sections = {}
        for s in cfg.sections():
            if s != "standards":
                sections[s] = 1

        standards = [(splitto(cfg.get("standards", o), ".", 2)[0], o)
                     for o in cfg.options("standards")]
        standards.sort()

        headers = []
        for _, s in standards:
            headers.extend(sorthdr(cfg.options(s)))
            del sections[s]

        if sections:
            raise RuntimeError("%s: sections without standards tags: %s"
                               % (fname, " ".join(sections.keys())))

        self.headers = headers

    def load_deps(self, fname):
        """Load the header-header and header-special dependency lists from
           config/prereqs.ini.  Like load_headers, we do not instantiate
           Header or SpecialDependency objects at this time."""
        cfg = ConfigParser.ConfigParser()
        cfg.read(fname)

        self.normal_deps = {}
        for h in cfg.options("prerequisites"):
            self.normal_deps[h] = cfg.get("prerequisites", h, raw=1).split()

        self.special_deps = {}
        for h in cfg.options("special"):
            if self.normal_deps.has_key(h):
                raise RuntimeError("%s: %s appears in both [prerequisites] "
                                   "and [special]" % (fname, h))
            self.special_deps[h] = cfg.get("special", h, raw=1)

    def load_known_errors(self, fname):
        """Load the specifications of all known errors from
           config/errors.ini."""
        self.errors_fname = fname
        cfg = ConfigParser.ConfigParser()
        cfg.read(fname)

        errors_by_tag = {}
        errors_by_header = {}
        for tag in cfg.sections():
            if cfg.has_option(tag, "header"):
                headers = cfg.get(tag, "header").split()
            else:
                headers = ["*"]
            if cfg.has_option(tag, "caution"):
                caution = int(cfg.get(tag, "caution"))
            else:
                caution = 0
            err = KnownError(tag, headers,
                             cfg.get(tag, "regexp"),
                             cfg.get(tag, "desc"),
                             caution)
            errors_by_tag[tag] = err
            for h in headers:
                if errors_by_header.has_key(h):
                    errors_by_header[h].append(err)
                else:
                    errors_by_header[h] = [err]
        self.errors_by_tag = errors_by_tag
        self.errors_by_header = errors_by_header

    def is_known_error(self, msg, header):
        """If MSG contains known error(s) for HEADER, return the tag(s) for
           those error(s), otherwise return None."""
        errs = {}
        candidates = (self.errors_by_header.get(header, []) +
                      self.errors_by_header.get("*", []))
        for line in msg:
            for err in candidates:
                if err.search(line):
                    if not errs.has_key(err.name):
                        errs[err.name] = err

        if len(errs) > 0:
            return errs.values()
        return None

    def load_content_tests(self, dname):
        """Load the specifications of all content tests."""
        content_tests = {}
        for f in glob.glob(os.path.join(dname, "*.ini")):
            if os.path.basename(f) == "CATEGORIES.ini": continue
            dt = TestProgram(f)
            if content_tests.has_key(dt.header):
                sys.stderr.write("%s: skipping extra test for %s\n"
                                 % (f, dt.header))
            content_tests[dt.header] = dt
        self.content_tests = content_tests

        self.required_modules = {"": 1}
        parser = ConfigParser.ConfigParser()
        parser.read(os.path.join(dname, "CATEGORIES.ini"))
        if parser.has_section("required_modules"):
            for m in parser.options("required_modules"):
                self.required_modules[m] = 1


class Dataset:
    """A Dataset instance represents the totality of information known
       about header files on this platform.  It is primarily a dictionary
       of { filename : Header instance } mappings, but also handles certain
       whole-dataset operations."""

    def __init__(self, cfg, mode):
        self.cfg = cfg
        self.mode = mode

        self.headers = {}
        for h in cfg.headers:
            self.headers[h] = Header(h, self.cfg, self)

        self.deps = {}
        for name, deplist in cfg.normal_deps.items():
            self.deps[self.headers[name]] = [self.headers[d] for d in deplist]
        for name, text in cfg.special_deps.items():
            h = self.headers[name]
            assert not self.deps.has_key(h)
            self.deps[h] = [SpecialDependency(name, text)]

    def get_header(self, name):
        if self.headers.has_key(name):
            return self.headers[name]
        raise RuntimeError("unknown header %s, check headers.ini" % name)

    def test_conflicts(self, cc, log):
        """Conflict testing is done _en masse_ after all available headers
           have been identified, for two reasons.  First, on some systems
           conflicts between two headers are only evident (provoke a compiler
           error) in one of the two possible #include orders.  Second,
           conflict testing is more expensive than all the rest of the tests
           put together.  We have gone to considerable algorithmic effort to
           minimize the number of compiler invocations required, and the
           algorithm is most efficient when operating on large batches of
           headers (assuming conflicts are rare)."""

        log.begin_test("conflict test, mode " + str(self.mode))

        # Construct a conflict matrix for every known header which is
        # compatible with this compilation mode.
        headers = []
        for h in self.headers.values():
            if h.presence != h.PRESENT: continue
            if h.caution == 1: continue
            assert h.depends is not None
            headers.append(h)

        matrix = ConflictMatrix(self, headers, log)
        matrix.find_conflicts(cc)

        for h in sorthdr(self.headers.keys()):
            self.headers[h].log_conflicts(log)

        log.end_test("done")

def main(argv):
    def usage():
        raise SystemExit("usage: %s ['compiler_id' | headers...] [-- cc [args]]"
                         % sys.argv[0])

    headers = None
    for i in range(len(argv)):
        if argv[i] == "--":
            if i == len(argv)-1:
                usage()
            headers = argv[1:i]
            cccmd = argv[i+1:]
            break
    else:
        if len(argv) > 1:
            headers = argv[1:]
        ccmd = ["cc"]

    cfg = Configuration("config", "content_tests")
    if not headers:
        headers = cfg.headers

    if headers[0] == "compiler_id":
        if len(headers) > 1: usage()

    log = Logger("st.log", verbose=0, progress=1)
    md = Metadata(cfg, log)

    cc = md.probe_compiler(ccmd)
    md.probe_runtime()
    if headers[0] == "compiler_id":
        md.report(sys.stdout)
        return

    md.smoke_test()

    datasets = [Dataset(cfg, CompilationMode(conform=0)),
                Dataset(cfg, CompilationMode(conform=1))]

    for h in headers:
        hh0 = datasets[0].get_header(h)
        for dset in datasets:
            if hh0.presence != hh0.ABSENT:
                hh = dset.get_header(h)
                hh.test(cc, log)
            if log.error_occurred:
                raise SystemExit(1)

    for dset in datasets:
        dset.test_conflicts(cc, log)
        if log.error_occurred:
            raise SystemExit(1)

    for dset in datasets:
        sys.stdout.write(str(dset.mode) + "\n")
        kk = dset.headers.items()
        try:
            kk.sort(key=lambda k: hsortkey(k[0]))
        except (NameError, TypeError):
            kk = [(hsortkey(k[0]), k[0], k[1]) for k in kk]
            kk.sort()
            kk = [(k[1], k[2]) for k in kk]
        for _, h in kk:
            if h.presence != h.UNKNOWN:
                h.output(sys.stdout)

if __name__ == '__main__':
    main(sys.argv)
