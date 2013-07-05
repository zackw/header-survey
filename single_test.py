#! /usr/bin/env python

# Copyright 2013 Zack Weinberg <zackw@panix.com> and other contributors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# There is NO WARRANTY.


# Compiler detection and identification - temporarily broken out of
# scansys for prototyping.

import ConfigParser
import StringIO
import errno
import locale
import os
import random
import re
import string
import sys

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

# At some point in the 2.x series, match.group(N) changed from returning
# -1 to returning None if the group was part of an unmatched alternative.
# Also reject the empty string (this can be returned on a successful match,
# but is never what we want in context).
def group_matched(grp):
    return grp is not None and grp != -1 and grp != ""

def delete_if_exists(fname):
    """Delete FNAME; do not raise an exception if FNAME already
       doesn't exist.  Used to clean up files that may or may not
       have been created by a compile invocation."""
    if fname is None:
        return
    try:
        os.remove(fname)
    except EnvironmentError, e:
        if e.errno != errno.ENOENT:
            raise

# opening a file in "rU" mode on a Python that doesn't support it
# ... silently succeeds!  So we can't use it at all.  Regex time!
_universal_readlines_re = re.compile("\r\n|\r|\n")
def universal_readlines(fname):
    f = open(fname, "rb")
    s = f.read().strip()
    f.close()
    if s == "": return []
    return _universal_readlines_re.split(s)

# Create a scratch file, with a unique name, in the current directory.
# 2.0 `tempfile` does not have NamedTemporaryFile, and doesn't have
# anything useful for defining it, either.  This is kinda sorta like
# the code implementing 2.7's NamedTemporaryFile.  Caller is
# responsible for cleaning up.
def named_tmpfile(prefix="tmp", suffix="txt"):
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
            # give up after ten thousand iterations
            if tries == 10000:
                raise
            # otherwise loop

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

def prepare_environment(ccenv):
    """Prepare the environment for compiler invocation."""
    for k, v in ccenv.items():
        os.environ[k] = v

    # Force the locale to "C" both for this process and all subsequently
    # invoked subprocesses.
    for k in os.environ.keys():
        if k[:3] == "LC_" or k[:4] == "LANG":
            del os.environ[k]
    os.environ["LANG"] = "C"
    os.environ["LANGUAGE"] = "C"
    os.environ["LC_ALL"] = "C"

    locale.setlocale(locale.LC_ALL, "C")

    # Redirect standard input from /dev/null in subprocesses.
    try:
        devnull = os.devnull
    except AttributeError:
        if os.platform == 'nt':
            devnull = "nul:"
        else:
            devnull = "/dev/null"
    fd = os.open(os.devnull, os.O_RDONLY)
    os.dup2(fd, 0)
    os.close(fd)

def invoke(argv):
    """Invoke the command in 'argv' and capture its output."""
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

    return (rc, msg)

# end of old-Python compatibility workarounds

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

def old_compiler_id(cc):
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

        ccid = " | ".join(results)
        if len(ccid) > 0:
            return ccid
    return "unidentified"

class Compiler:
    """A Compiler instance knows how to invoke a particular compiler
       on provided source code.  Instantiated from a command + arguments,
       it will identify the compiler and set up to use it.

       Uses a config file (defaulting to 'compilers.ini') to track the
       idiosyncracies of various compilers."""

    def __init__(self, base_cmd, cfgf="compilers.ini"):
        self.base_cmd = base_cmd

        cfg = ConfigParser.ConfigParser()
        cfg.read(cfgf)

        (compiler, label) = self.identify(cfg, cfgf)
        self.compiler = compiler
        self.label = label

        self.notfound_re = re.compile(cfg.get(compiler, "notfound_re"),
                                      re.VERBOSE)

        self.preproc_cmd = cfg.get(compiler, "preproc").split()
        self.preproc_out = cfg.get(compiler, "preproc_out")
        self.compile_cmd = cfg.get(compiler, "compile").split()
        self.compile_out = cfg.get(compiler, "compile_out")

        self.define_opt  = cfg.get(compiler, "define")
        self.conform_opt = cfg.get(compiler, "conform").split()
        self.thread_opt = cfg.get(self.compiler, "threads").split()
        self.test_with_thread_opt = 0

        self.smoke_test(cfg, cfgf)
        self.conformance_test(cfg, cfgf)

    def subst_filename(self, fname, opts):
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

    def fatal(self, msg, output):
        sys.stderr.write("Fatal error: %s\n" % msg)
        for line in output:
            sys.stderr.write("| %s\n" % line)
        raise SystemExit(1)

    def failure_due_to_nonexistence(self, msg, header):
        for m in msg:
            if self.notfound_re.search(m) and m.find(header) != -1:
                return 1
        return 0

    def test_invoke(self, code, suffix, action, outname,
                    conform=0, thread=0, opts=[], defines=[]):
        cmd = self.base_cmd[:]
        if conform:
            cmd.extend(self.conform_opt)
        if thread:
            cmd.extend(self.thread_opt)
        cmd.extend(opts)
        if len(defines) > 0:
            for d in defines:
                cmd.append(self.define_opt + d)

        test_c = None
        test_s = None
        try:
            test_c = named_tmpfile(prefix="cct", suffix=suffix)
            test_s = self.subst_filename(test_c, outname)
            cmd.extend(self.subst_filename(test_c, action))
            cmd.append(test_c)

            f = open(test_c, "w")
            f.write(code)
            f.write("\n")
            f.close()

            (rc, msg) = invoke(cmd)
            if rc != 0:
                msg.append("failed program was:")
                msg.extend(["| %s" % l for l in code.split("\n")])
            return (rc, msg)
        finally:
            delete_if_exists(test_c)
            delete_if_exists(test_s)

    def test_compile(self, code, conform=0, thread=0, opts=[], defines=[]):
        return self.test_invoke(code, "c",
                                self.compile_cmd,
                                self.compile_out,
                                conform, thread, opts, defines)

    def test_preproc(self, code, conform=0, thread=0, opts=[], defines=[]):
        return self.test_invoke(code, "c",
                                self.preproc_cmd,
                                self.preproc_out,
                                conform, thread, opts, defines)

    def identify(self, cfg, cfgf):
        """Identify the compiler in use."""

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

        # Construct a source file that will fail to compile with
        # exactly one #error directive, identifying the compiler in
        # use.  We do it this way because at this point we have no
        # control over compilation mode or output; an #error will
        # reliably produce an error message that invoke() knows how
        # to capture, and no output file.
        compilers = []
        for sect in cfg.sections():
            # Some compilers are imitated - their identifying macros are
            # also defined by other compilers.  Sort these to the end.
            imitated = cfg.has_option(sect, "imitated")
            compilers.append((imitated, cfg.get(sect, "id_macro"), sect))
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
            f.write("#else\n#error UNKNOWN\n#endif")
            f.close()

            (rc, msg) = invoke(self.base_cmd + [test1])
            compiler = parse_output(msg, compilers)

            if compiler == "FAIL":
                self.fatal("unable to parse compiler output.", msg)
            if compiler == "UNKNOWN":
                self.fatal("no configuration available for this "
                           "compiler.  Please add appropriate settings "
                           "to " + repr(cfgf) + ".", [])

            # Confirm the identification.
            version_argv = cfg.get(compiler, "version").split()
            version_out = cfg.get(compiler, "version_out")

            for arg in version_argv:
                if arg.startswith("$."):
                    test2 = named_tmpfile(prefix="cci", suffix=arg[2:])
                    f = open(test2, "w")
                    f.write("int dummy;")
                    f.close()
                    test2_o  = self.subst_filename(test2, version_out)
                    version_argv = self.subst_filename(test2, version_argv)
                    break

            (rc, msg) = invoke(self.base_cmd + version_argv)
            if rc != 0:
                self.fatal("detailed version request failed", msg)
            mm = "\n".join(msg[1:]) # throw away the command line
            version_re = re.compile(cfg.get(compiler, "id_regexp"),
                                    re.VERBOSE|re.DOTALL)
            match = version_re.search(mm)
            if not match:
                self.fatal("version information not as expected: "
                           "is this really " + compiler + "?", msg)

            try:
                version = match.group("version")
            except IndexError:
                versio1 = match.group("version1")
                versio2 = match.group("version2")
                if group_matched(versio1): version = versio1
                elif group_matched(versio2): version = versio2
                else:
                    self.fatal("version number not found", msg)

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
                return (compiler, "%s %s (%s)" % (compiler, version, details))
            else:
                return (compiler, "%s %s" % (compiler, version))

        finally:
            if test1   is not None: delete_if_exists(test1)
            if test2   is not None: delete_if_exists(test2)
            if test2_o is not None: delete_if_exists(test2_o)


    def smoke_test(self, cfg, cfgf):
        """Tests which, if they fail, indicate something horribly
           wrong with the compiler and/or our usage of it.
           Either returns successfully, or issues a fatal error."""

        test_modes = [
            (self.test_preproc, 0, "preprocess"),
            (self.test_preproc, 1, "preprocess (conformance mode)"),
            (self.test_compile, 0, "compile"),
            (self.test_compile, 1, "compile (conformance mode)")
        ]

        # This code should compile without complaint.
        for (action, conform, tag) in test_modes:
            (rc, msg) = self.test_compile("#include <stdarg.h>\nint dummy;",
                                          conform)
            if rc != 0:
                self.fatal("failed to %s simple test program. "
                           "Check configuration for %s in %s."
                           % (tag, self.compiler, cfgf), msg)

        # This code should _not_ compile, in any mode, nor should it
        # preprocess.
        for (action, conform, tag) in test_modes:
            (rc, msg) = action("#include <nonexistent.h>\nint dummy;", conform)
            if rc == 0 or not self.failure_due_to_nonexistence(msg,
                                                               "nonexistent.h"):
                self.fatal("failed to detect nonexistence of <nonexistent.h>"
                           " (%s). Check configuration for %s in %s."
                           % (tag, self.compiler, cfgf), msg)

    def probe_max_std(self, label, probes, testcode):
        """Subroutine of conformance_test.
           PROBES is a list of tuples: (compiler options, macros to
           define, expected value). For the first such tuple that
           makes TESTCODE preprocess successfully, return a slightly
           munged version of the options+defines."""

        failures = []
        for (opts, defines, expected) in probes:
            if opts == "no":
                continue
            if opts == "":
                opts = []
            else:
                opts = opts.split()
            if defines != "":
                opts.extend([self.define_opt + d for d in defines.split()])

            (rc, msg) = self.test_preproc(testcode, conform=1, opts=opts,
                                          defines=["EXPECTED="+expected])
            if rc == 0:
                return opts

            failures.append("")
            failures.extend(msg)

        self.fatal("all %s version tests failed." % label, msg)

    def conformance_test(self, cfg, cfgf):
        """Determine the levels of the C, POSIX, and XSI standards to
           which this compiler + target OS claim to conform; adjust
           'conform_opt' accordingly.  Also figure out whether
           threaded code must be compiled in a special mode."""

        # First find and activate the newest supported C standard.
        self.conform_opt.extend(self.probe_max_std("C", [
                (cfg.get(self.compiler, "c2011"), "", "201112L"),
                (cfg.get(self.compiler, "c1999"), "", "199901L"),
                # There are two possible values of __STDC_VERSION__ for C1989.
                (cfg.get(self.compiler, "c1989"), "EXPECTED2=1", "199401L")
                ], r"""
#if __STDC_VERSION__ != EXPECTED && \
    (!defined EXPECTED2 || __STDC_VERSION__ != EXPECTED2)
#error "wrong version"
#endif"""))

        # If we have unistd.h, also find and activate the newest supported
        # POSIX standard.
        (rc, msg) = self.test_preproc("#include <unistd.h>\nint dummy;\n")
        if rc != 0 and not self.failure_due_to_nonexistence(msg, "unistd.h"):
            self.fatal("failed to determine presence of <unistd.h>. "
                       "Check configuration for %s in %s."
                       % (self.compiler, cfgf), msg)
        if rc == 0:
            # If _XOPEN_SOURCE works, we want to use it instead of
            # _POSIX_C_SOURCE, as it may enable more stuff.
            #
            # Some systems (e.g. NetBSD) support _XOPEN_SOURCE as input to
            # feature selection but don't bother defining _XOPEN_VERSION in
            # response.  They _do_, however, respond with the appropriate
            # _POSIX_VERSION definition.
            #
            # So for each _POSIX_VERSION level we are interested in, try
            # selecting it first with _XOPEN_SOURCE and then, if that didn't
            # work, with _POSIX_C_SOURCE.
            #
            # There were meaningful values of _XOPEN_SOURCE and _POSIX_C_SOURCE
            # prior to 500 / 199506L, but they are so old that probing for them
            # is not worth the trouble.
            #
            # The very last trial doesn't even include unistd.h, in case the
            # failures are because it doesn't exist.
            self.conform_opt.extend(self.probe_max_std("POSIX", [
                    ("", "_XOPEN_SOURCE=700",       "200809L"),
                    ("", "_POSIX_C_SOURCE=200809L", "200809L"),
                    ("", "_XOPEN_SOURCE=600",       "200112L"),
                    ("", "_POSIX_C_SOURCE=200112L", "200112L"),
                    ("", "_XOPEN_SOURCE=500",       "199506L"),
                    ("", "_POSIX_C_SOURCE=199506L", "199506L"),
                    ("", "",                        "0"),
                ], r"""
#if EXPECTED != 0
#include <unistd.h>
#if _POSIX_VERSION != EXPECTED
#error "wrong version"
#endif
#endif"""))

        # Find out whether code that includes <pthread.h> must be
        # compiled in a special mode.  If so, enabling this mode may
        # change prerequisite sets, so we have to test both ways.
        (rc, msg) = self.test_compile("#include <pthread.h>\nint dummy;\n")
        if rc != 0 and not self.failure_due_to_nonexistence(msg, "pthread.h"):
            (rc, msg2) = self.test_compile("#include <pthread.h>\nint dummy;",
                                           thread=1)
            if rc == 0:
                self.test_with_thread_opt = 1
            else:
                self.fatal("pthread.h exists but cannot be compiled? "
                           "Check configuration for %s in %s."
                           % (self.compiler, cfgf),
                           msg + msg2)

    def report(self, outf):
        outf.write("old: %s\n" % old_compiler_id(self.base_cmd))
        outf.write("new: %s\n" % self.label)
        outf.write("conformance options: %s\n" % " ".join(self.conform_opt))
        outf.write("repeat tests with threads: %d\n"
                   % self.test_with_thread_opt)

class KnownError:
    """One potential failure mode for a header file."""
    def __init__(self, tag, headers, regexp, desc, caution):
        self.tag = tag
        self.headers = headers
        self.regexp = re.compile(regexp, re.VERBOSE)
        self.desc = desc
        self.caution = caution

    def search(self, msg):
        return self.regexp.search(msg)

    def output(self, outf):
        outf.write("$E %s\n" % self.tag)

class ConflictAnn:
    """Conflict annotation for a header file."""
    def __init__(self, conflicts):
        self.conflicts = conflicts

    def output(self, outf):
        outf.write("$C %s\n" % " ".join([h.name for h in self.conflicts]))

class SpecialDependency:
    """Used to represent [special] dependencies from prereqs.ini.
       Stubs some Header methods and properties so it can be treated
       like one when convenient."""

    PRESENT = ''

    def __init__(self, header, text):
        self.name = header
        self.text = text
        self.presence = self.PRESENT

    def gen_includes(self, outf, conform, thread):
        outf.write(self.text)
        outf.write("\n")

    def test(self, cc):
        pass

class Header:
    """A Header instance represents everything that is currently known
       about a single header file, and knows how to carry out a sequence
       of tests of the header:

         - whether it exists at all
         - whether it can be preprocessed successfully, in isolation
         - whether it can be compiled successfully, in isolation:
           - in the default compilation mode
           - in the strict conformance mode
           - (optionally) with thread support enabled, in both the above modes
         - if it can't be compiled successfully in isolation in any
           of the above modes, whether this can be fixed by including
           other headers first

       Information about other headers to try including first is stored
       in the configuration file 'prereqs.ini', q.v."""

    # State codes as written to the file.  Some of these are also used
    # for internal flags.
    UNKNOWN    = '?'
    ABSENT     = '-'
    BUGGY      = '!'

    PRESENT    = ''
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

    def __init__(self, name, dataset):
        self.name = name
        self.dataset = dataset
        self.dataset.headers[name] = self
        self.annotations  = []

        # prereqs lists form a 2x2 matrix indexed by [conform][thread].
        # initially all are empty.
        self.prereqs = [ [ [], [] ],
                         [ [], [] ] ]

        # caution likewise
        self.caution = [ [ 0, 0 ],
                         [ 0, 0 ] ]

        self.pref_mode = None # will be set to a 2-tuple by test_depends

        self.presence = self.UNKNOWN # can be ABSENT, BUGGY, PRESENT
        self.contents = self.UNKNOWN # can be PRESENT, INCOMPLETE, CORRECT
        self.depends  = None # None=unknown, 0=no, 1=yes
        self.conflict = None # None=unknown, 0=no, 1=yes

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def debug_dump(self, outf):
        outf.write("%s = %s\n" % (self.name, self.state_label()))
        outf.write("   presence: " + self.STATE_LABELS[self.presence] + "\n")
        outf.write("   contents: " + self.STATE_LABELS[self.contents] + "\n")
        outf.write("    depends: " + repr(self.depends) + "\n")
        outf.write("   conflict: " + repr(self.conflict) + "\n")
        outf.write("  pref_mode: " + repr(self.pref_mode) + "\n")
        outf.write("    caution: [..]=%d [c.]=%d [.t]=%d [ct]=%d\n"
                   % (self.caution[0][0],
                      self.caution[1][0],
                      self.caution[0][1],
                      self.caution[1][1]))
        outf.write("   deplists:\n")
        outf.write("     [..] = %s\n"
                   % " ".join([h.name for h in self.prereqs[0][0]]))
        outf.write("     [c.] = %s\n"
                   % " ".join([h.name for h in self.prereqs[1][0]]))
        outf.write("     [.t] = %s\n"
                   % " ".join([h.name for h in self.prereqs[0][1]]))
        outf.write("     [ct] = %s\n"
                   % " ".join([h.name for h in self.prereqs[1][1]]))
        outf.write("  annotations:\n")
        for a in self.annotations:
            outf.write("  ")
            a.output(outf)
        outf.write("\n")

    def state_code(self):
        if self.presence != self.PRESENT:
            # unknown/absent/buggy exclude all other indicators.
            return self.presence
        else:
            # Confirm we have done all the tests.
            assert self.depends is not None
            assert self.conflict is not None

            caution = (self.conflict or
                       self.caution[0][0] or self.caution[0][1] or
                       self.caution[1][0] or self.caution[1][1])

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
        self.output_depends(outf)
        for ann in self.annotations:
            ann.output(outf)

    def output_depends(self, outf):
        if not self.depends: return

        def output_1(outf, lst, tag=""):
            if tag != "":
                tag = " [%s]" % tag
            if len(lst) == 0: return
            if isinstance(lst[0], SpecialDependency):
                assert len(lst) == 1
                outf.write("$S%s %s\n" % (tag, lst[0].name))
            else:
                outf.write("$P%s %s\n" % (tag, " ".join([h.name for h in lst])))

        output_1(outf, self.prereqs[0][0])

        # output other dependency lists only if they are different from [0][0]
        if self.prereqs[1][0] != self.prereqs[0][0]:
            output_1(outf, self.prereqs[1][0], "conform")
        if self.prereqs[0][1] != self.prereqs[0][0]:
            output_1(outf, self.prereqs[1][0], "thread")
        if self.prereqs[1][1] != self.prereqs[0][0]:
            output_1(outf, self.prereqs[1][1], "conform,thread")

    def gen_includes(self, outf, conform, thread):
        if self.presence != self.PRESENT: return
        for h in self.prereqs[conform][thread]:
            h.gen_includes(outf, conform, thread)
        outf.write("#include <%s>\n" % self.name)

    def test(self, cc):
        """Perform all checks on this header.  This blindly calls
           itself on other header objects, and so must be idempotent
           (which is handled in each subroutine, so *they* are all
           idempotent as well)"""

        self.test_presence(cc)
        self.test_depends(cc)
        self.test_conflict(cc)
        self.test_contents(cc)

    def test_presence(self, cc):
        if self.presence != self.UNKNOWN: return

        (rc, msg) = cc.test_preproc("#include <%s>" % self.name)
        if rc == 0:
            self.presence = self.PRESENT
            return
        if cc.failure_due_to_nonexistence(msg, self.name):
            self.presence = self.ABSENT
            return

        errs = self.dataset.is_known_error(msg, self.name)
        if errs is not None:
            # caution vs error is ignored at this point; any problem is fatal.
            self.presence = self.BUGGY
            self.annotations.extend(errs)
            return

        cc.fatal("unrecognized failure mode for <%s>. "
                 "Please investigate and add an entry to %s."
                 % (self.name, self.dataset.errors_fname), msg)

    def test_depends_1(self, cc, possible_prereqs, conform, thread):
        failures = []

        # prereq_combs is guaranteed to produce an empty set as the first
        # item in its returned list, and the complete set as the last item.
        for candidate_set in prereq_combs(possible_prereqs):
            buf = StringIO.StringIO()
            for h in candidate_set:
                h.gen_includes(buf, conform, thread)
            buf.write("#include <%s>\n" % self.name)
            buf.write("int avoid_empty_translation_unit;\n")

            (rc, msg) = cc.test_compile(buf.getvalue(),
                                        conform=conform,
                                        thread=thread)
            if rc == 0:
                self.prereqs[conform][thread] = candidate_set
                return 1

            if len(failures) > 0: failures.append("")
            failures.extend(msg)

        # If we get here, there is a serious problem.
        # Look for a known bug in the last set of messages, which will be
        # the maximal prerequisite set and therefore the least likely to have
        # problems.
        errs = self.dataset.is_known_error(msg, self.name)
        if errs is not None:
            self.annotations.extend(errs)
            for e in errs:
                if e.caution:
                    self.caution[conform][thread] = 1
                else:
                    self.presence = self.BUGGY
            return 0

        cc.fatal("unrecognized failure mode for <%s>. "
                 "Please investigate and add an entry to %s."
                 % (self.name, self.dataset.errors_fname), msg)

    def test_depends(self, cc):
        if self.depends is not None: return
        if self.presence != self.PRESENT: return

        possible_prereqs = []
        for h in self.dataset.prereqs.get(self.name, []):
            h.test(cc)
            if h.presence == h.PRESENT:
                possible_prereqs.append(h)

        self.test_depends_1(cc, possible_prereqs, 0, 0)
        if self.presence == self.BUGGY: return
        self.test_depends_1(cc, possible_prereqs, 1, 0)
        if self.presence == self.BUGGY: return
        if cc.test_with_thread_opt:
            self.test_depends_1(cc, possible_prereqs, 0, 1)
            if self.presence == self.BUGGY: return
            self.test_depends_1(cc, possible_prereqs, 1, 1)
            if self.presence == self.BUGGY: return
        else:
            self.prereqs[0][1] = self.prereqs[0][0][:]
            self.prereqs[1][1] = self.prereqs[1][0][:]

            self.caution[0][1] = self.caution[0][0]
            self.caution[1][1] = self.caution[1][0]

        self.depends = (len(self.prereqs[0][0]) > 0 or
                        len(self.prereqs[0][1]) > 0 or
                        len(self.prereqs[1][0]) > 0 or
                        len(self.prereqs[1][1]) > 0)

        # Find a mode in which this header can be processed without errors.
        if not self.caution[1][0]: # conform, no threads
            self.pref_mode = (1, 0)
        elif not self.caution[1][1]: # conform, threads
            self.pref_mode = (1, 1)
        elif not self.caution[0][0]: # no conform, no threads
            self.pref_mode = (0, 0)
        elif not self.caution[0][1]: # no conform, threads
            self.pref_mode = (0, 1)
        else:
            # There is no mode without problems.
            self.presence = self.BUGGY

    def test_pairwise_conflict(self, cc, others):
        # Test every pair of headers in 'others' for a conflict with
        # this header.  FUTURE: This is O(N) compiler invocations,
        # which can get quite slow; maybe do a binary chop instead.
        (conform, thread) = self.pref_mode
        conflicts = []
        buf = StringIO.StringIO()
        for h in others:
            buf.seek(0)
            h.gen_includes(buf, conform, thread)
            self.gen_includes(buf, conform, thread)
            buf.write("int avoid_empty_translation_unit;\n")
            buf.truncate()

            (rc, msg) = cc.test_compile(buf.getvalue(),
                                        conform=conform, thread=thread)
            if rc != 0:
                conflicts.append(h)

        return conflicts

    def test_conflict(self, cc):
        if self.conflict is not None: return
        if self.presence != self.PRESENT: return

        (conform, thread) = self.pref_mode

        # Compute a list of every other known header whose dependencies
        # have been calculated and which is compatible with this header's
        # preferred compilation mode.  Distinguish between headers that
        # don't have any conflicts already, and those that do.
        others = []
        conflicted = []
        conflicts = []
        for h in self.dataset.headers.values():
            if   (h != self and h.presence == h.PRESENT and
                  h.depends is not None and
                  not h.caution[conform][thread]):
                if not h.conflict:
                    others.append(h)
                else:
                    conflicted.append(h)

        # As an optimization, test whether this header can be
        # included, twice, after all the 'others'. If this works, we
        # can safely assume there are no pairwise conflicts with that
        # set; otherwise we have to go row by row.
        buf = StringIO.StringIO()
        for h in others:
            h.gen_includes(buf, conform, thread)
        self.gen_includes(buf, conform, thread)
        self.gen_includes(buf, conform, thread)
        buf.write("int avoid_empty_translation_unit;\n")
        (rc, msg) = cc.test_compile(buf.getvalue(),
                                    conform=conform, thread=thread)
        if rc != 0:
            conflicts.extend(self.test_pairwise_conflict(cc, [self]))
            conflicts.extend(self.test_pairwise_conflict(cc, others))

        # Headers that have some conflict already can't be tested in a
        # big lump.
        conflicts.extend(self.test_pairwise_conflict(cc, conflicted))

        if len(conflicts) == 0:
            if rc != 0:
                cc.fatal("No pairwise conflict detected for %s" % self.name,
                         msg)
            self.conflict = 0
            return

        self.conflict = 1
        self.annotations.append(ConflictAnn(conflicts))

        # Conflicts are mutual; annotate the other headers as well.
        for h in conflicts:
            h.conflict = 1
            found = 0
            for a in h.annotations:
                if isinstance(a, ConflictAnn):
                    a.conflicts.append(self)
                    found = 1
                    break
            if not found:
                h.annotations.append(ConflictAnn([self]))

    def test_contents(self, cc):
        if self.presence != self.PRESENT: return
        self.contents = self.PRESENT

class Dataset:
    """A Dataset instance represents the totality of information known
       about header files on this platform.  It is primarily a dictionary
       of { filename : Header instance } mappings, but also stores shared
       configuration data and some utility methods."""

    def __init__(self):
        self.headers = {}
        self.prereqs_fname = "prereqs.ini"
        self.errors_fname = "errors.ini"
        self.load_prereqs(self.prereqs_fname)
        self.load_errors(self.errors_fname)

    def load_prereqs(self, fname):
        cfg = ConfigParser.ConfigParser()
        cfg.read(fname)
        prereqs = {}
        for h in cfg.options("prerequisites"):
            prereqs[h] = [Header(p, self)
                          for p in cfg.get("prerequisites", h).split()]

        for h in cfg.options("special"):
            if prereqs.has_key(h):
                raise RuntimeError("%s: %s appears in both [prerequisites] "
                                   "and [special]" % (fname, h))
            prereqs[h] = [SpecialDependency(h, cfg.get("special", h))]

        self.prereqs = prereqs

    def load_errors(self, fname):
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
        errs = {}
        candidates = (self.errors_by_header.get(header, []) +
                      self.errors_by_header.get("*", []))
        for line in msg:
            for err in candidates:
                if err.search(line):
                    if not errs.has_key(err.tag):
                        errs[err.tag] = err

        if len(errs) > 0:
            return errs.values()
        return None

if __name__ == '__main__':
    def usage(argv):
        raise SystemExit("usage: %s (compiler_id|header.h...) "
                         "[-- cc [ccargs...]]"
                         % argv[0])

    def main(argv, stdout):
        if len(argv) < 2: usage()

        prepare_environment({})

        if argv[1] == "compiler_id":
            if len(argv) == 2:
                cc = Compiler(["cc"])
            elif argv[2] == "--":
                cc = Compiler(argv[3:])
            else:
                cc = Compiler(argv[2:])
            cc.report(stdout)
        else:
            headers = None
            for i in range(len(argv)):
                if argv[i] == "--":
                    if i == 1 or i == len(argv)-1:
                        usage()
                    headers = argv[1:i]
                    cc = Compiler(argv[i+1:])
                    break
            if headers == None:
                headers = argv[1:]
                cc = Compiler(["cc"])

            dataset = Dataset()
            for h in headers:
                sys.stderr.write("# %s\n" % h)
                hh = Header(h, dataset)
                hh.test(cc)
                hh.debug_dump(sys.stderr)

            kk = dataset.headers.items()
            try:
                kk.sort(key=lambda k: hsortkey(k[0]))
            except (NameError, TypeError):
                kk = [(hsortkey(k[0]), k[0], k[1]) for k in kk]
                kk.sort()
                kk = [(k[1], k[2]) for k in kk]
            for _, h in kk:
                if h.presence != h.UNKNOWN:
                    h.output(stdout)

    main(sys.argv, sys.stdout)
