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

def delete_if_exists(fname):
    """Delete FNAME; do not raise an exception if FNAME already
       doesn't exist.  Used to clean up files that may or may not
       have been created by a compile invocation."""
    try: os.remove(fname)
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
# the code implementing 2.7's NamedTemporaryFile.
_named_tmpfile_cwd = None
_named_tmpfile_letters = "abcdefghijklmnopqrstuvwxyz012345" # 32 characters
def named_tmpfile(prefix="tmp", suffix="txt"):
    global _named_tmpfile_cwd
    global _named_tmpfile_letters
    if _named_tmpfile_cwd is None:
        _named_tmpfile_cwd = os.getcwd()

    tries = 0
    while 1:
        candidate = "".join([random.choice(_named_tmpfile_letters)
                             for _ in (1,2,3,4,5)])
        path = os.path.join(_named_tmpfile_cwd,
                            prefix + candidate + "." + suffix)
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
        if result is not None:
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

def new_compiler_id_1(msg, compilers):
    # This is a separate routine just so we can use "return" to break out
    # of two loops at once.
    for line in msg:
        if line.find("error") != -1:
            for (imitated, macro, name) in compilers:
                if re.search(r'\b' + name + r'\b', line):
                    return name
            if re.search(r'\bUNKNOWN\b', line):
                return "UNKNOWN"
    return "FAIL"

def new_compiler_id(cc):
    data = ConfigParser.ConfigParser()
    data.read("compilers.ini")

    # Construct a source file that will fail to compile with exactly one
    # #error directive, identifying the compiler in use.
    compilers = []
    for sect in data.sections():
        # Some compilers are imitated - their identifying macros are
        # also defined by other compilers.  Sort these to the end.
        imitated = data.has_option(sect, "imitated")
        compilers.append((imitated, data.get(sect, "id_macro"), sect))
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

        (rc, msg) = invoke(cc + [test1])
        compiler = new_compiler_id_1(msg, compilers)

        if compiler == "FAIL":
            for line in msg: sys.stderr.write("| " + line.strip() + "\n")
            raise SystemExit("Unable to parse compiler output.")
        if compiler == "UNKNOWN":
            raise SystemExit("Unable to identify compiler.")

        # Confirm the identification.
        version_argv = data.get(compiler, "version").split()
        version_out = data.get(compiler, "version_out")

        for i in range(len(version_argv)):
            if version_argv[i].startswith("$."):
                test2 = named_tmpfile(prefix="cci", suffix=version_argv[i][2:])
                f = open(test2, "w")
                f.write("int dummy;")
                f.close()
                version_argv[i] = test2
                break

        if version_out != "":
            if version_out.startswith("$."):
                (root, ext) = os.path.splitext(test2)
                version_out = root + version_out[1:]
            test2_o = version_out

        (rc, msg) = invoke(cc + version_argv)
        if rc != 0:
            for line in msg: sys.stderr.write("| " + line.strip() + "\n")
            raise SystemExit("Detailed version request failed.")
        mm = "\n".join(msg[1:]) # throw away the command line
        version_re = re.compile(data.get(compiler, "id_regexp"),
                                re.VERBOSE|re.DOTALL)
        match = version_re.search(mm)
        if not match:
            for line in msg: sys.stderr.write("| " + line.strip() + "\n")
            raise SystemExit("Version information for " + compiler +
                             " not in expected format")

        try:
            version = match.group("version")
        except IndexError:
            versio1 = match.group("version1")
            versio2 = match.group("version2")
            if versio1 != -1: version = versio1
            elif versio2 != -1: version = versio2
            else:
                for line in msg: sys.stderr.write("| " + line.strip() + "\n")
                raise SystemExit("No version number found.")

        try:
            details = match.group("details")
        except IndexError:
            details = -1

        if details != -1:
            return (compiler, "%s %s (%s)" % (compiler, version, details))
        else:
            return (compiler, "%s %s" % (compiler, version))

    finally:
        if test1   is not None: delete_if_exists(test1)
        if test2   is not None: delete_if_exists(test2)
        if test2_o is not None: delete_if_exists(test2_o)

def probe_max_version(cmd, test_c, verre, nonexre, topts):
    found = None
    for opt in topts:
        if opt == "no":
            continue
        if opt == "":
            cmdline = cmd + [test_c]
        else:
            cmdline = cmd + [opt, test_c]
        (rc, msg) = invoke(cmdline)
        for line in msg:
            m = verre.search(line)
            if m:
                found = (m.group(1), opt)
                # Try not to return a zero version.
                if int(found[0]) != 0:
                    return found
            m = nonexre.search(line)
            if m:
                # If we got a failure because a file doesn't exist, give up.
                return ("0", "")

    # But we will return a zero version if we couldn't do any better.
    if found is not None:
        return found

    for line in msg: sys.stderr.write("| " + line.strip() + "\n")
    raise SystemExit("No version number found.")


def probe_max_c_and_xopen_versions(cc, compiler):
    data = ConfigParser.ConfigParser()
    data.read("compilers.ini")

    nonexre = re.compile(data.get(compiler, "notfound_re"))

    test_i = None
    test_c = None
    try:
        test_c = named_tmpfile(prefix="cci", suffix="c")
        (test_root, _) = os.path.splitext(test_c)

        test_i = data.get(compiler, "preproc_out")
        if test_i.startswith("$."):
            test_i = test_root + test_i[1:]

        preproc = data.get(compiler, "preproc").split()
        for i in range(len(preproc)):
            if preproc[i].startswith("$."):
                preproc[i] = test_root + preproc[i][1:]

        conform = data.get(compiler, "conform").split()

        cmdline = cc + conform + preproc

        f = open(test_c, "w")
        f.write("#if __STDC_VERSION__ >= 201112L\n"
                "#error C_2011\n"
                "#elif __STDC_VERSION__ >= 199901L\n"
                "#error C_1999\n"
                "#elif __STDC__ >= 1\n"
                "#error C_1989\n"
                "#else\n"
                "#error C_0\n"
                "#endif\n")
        f.close()

        cverre = re.compile(r"\berror\b.*C_([0-9]+)\b")
        (cver, copt) = probe_max_version(cmdline, test_c, cverre, nonexre,
                                         [data.get(compiler, "c2011"),
                                          data.get(compiler, "c1999"),
                                          data.get(compiler, "c1989"),
                                          ""])

        if copt != "":
            cmdline.append(copt)

        f = open(test_c, "w")
        f.write("#include <unistd.h>\n"
                "#if _POSIX_VERSION >= 200809L\n"
                "#error X_7\n"
                "#elif _POSIX_VERSION >= 200112L\n"
                "#error X_6\n"
                "#elif _POSIX_VERSION >= 199506L\n"
                "#error X_5\n"
                "#elif _POSIX_VERSION >= 199309L\n"
                "#error X_4\n"
                "#else\n"
                "#error X_0\n"
                "#endif\n")
        f.close()

        D = data.get(compiler, "define")

        xverre = re.compile(r"\berror\b.*X_([0-9])\b")
        (xver, xopt) = probe_max_version(cmdline, test_c, xverre, nonexre,
                                         [D+"_XOPEN_SOURCE=700",
                                          D+"_XOPEN_SOURCE=600",
                                          D+"_XOPEN_SOURCE=500",
                                          D+"_XOPEN_SOURCE=4",
                                          ""])
        (pver, popt) = probe_max_version(cmdline, test_c, xverre, nonexre,
                                         [D+"_POSIX_C_SOURCE=200809L",
                                          D+"_POSIX_C_SOURCE=200112L",
                                          D+"_POSIX_C_SOURCE=199506L",
                                          D+"_POSIX_C_SOURCE=199309L",
                                          D+"_POSIX_C_SOURCE=2",
                                          ""])

        if int(xver) >= int(pver):
            return (cver, copt, xver, xopt)
        else:
            return (cver, copt, pver, popt)

    finally:
        if test_c is not None: delete_if_exists(test_c)
        if test_i is not None: delete_if_exists(test_i)

if __name__ == '__main__':
    cc = sys.argv[1:]
    print "old:", old_compiler_id(cc)
    (compiler, label) = new_compiler_id(cc)
    print "new:", label
    (cver, copt, xver, xopt) = probe_max_c_and_xopen_versions(cc, compiler)
    print "C:  ", cver, copt
    print "X:  ", xver, xopt
