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
import errno
import locale
import os
import random
import re
import string
import sys

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

if __name__ == '__main__':
    Compiler(sys.argv[1:]).report(sys.stdout)
