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

def ct(conform, thread):
    """Subroutine of several class methods far below that need to be able
       to print a code for a "compilation mode", which is ostensibly a pair
       of booleans but has grown sufficient hair that it probably ought to
       be refactored into its own class or summat."""
    c = "."
    t = "."
    if conform: c = "c"
    if thread: t = "t"
    return "["+c+t+"]"

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

class LineCounter:
    """Wrap a file-like object open for writing, and keep track of the
       current line within that file.  It is assumed that the file is
       initially empty, and that you never change the file position."""
    def __init__(self, fh):
        self.fh = fh
        self.lineno = 1

    def write(self, text):
        self.fh.write(text)
        self.lineno = self.lineno + text.count("\n")

    def writelines(self, strings):
        for s in strings: self.write(s)

    def flush(self): self.fh.flush()
    def close(self): self.fh.close()

    def getvalue(self): return self.fh.getvalue()

#
# Code generation for decltests (used by Header.test_contents, far below)
# Note: all of this code requires that the file-like passed to generate()
# be a LineCounter instance.
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
       (see decltests/CATEGORIES.ini).  They all start out _enabled_, and
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

    def generate(self, outf):
        """Public interface to write the code for this test to OUTF.
           Subclasses should not need to tamper with this method."""
        if not self.enabled: return
        if self.name is None:
            self.lineno = outf.lineno
            self.name = "t_" + str(self.lineno)
        else:
            if self.lineno < outf.lineno:
                raise RuntimeError("%s (%s:%s): line numbers out of sync "
                                   " (want %d, already at %d)"
                                   % (self.tag, self.std, self.mod,
                                      self.lineno, outf.lineno))
            while outf.lineno < self.lineno:
                outf.write("\n")
        self._generate(outf)

    def _generate(self, outf):
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

    def _generate(self, outf):
        decl = mkdeclarator(self.dtype, self.name)
        if self.cond != "":
            if self.cond[0] == '?':
                outf.write("#if %s\n" % self.cond[1:])
            else:
                outf.write("#ifdef %s\n" % self.cond)
        if self.init == "":
            outf.write(decl + ";\n")
        else:
            outf.write("%s = %s;\n" % (decl, self.init))
        if self.cond != "":
            outf.write("#endif\n")

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

    def _generate(self, outf):
        # To declare a function that returns a function pointer without
        # benefit of typedefs, you write
        #   T (*fn(ARGS))(PROTO) { ... }
        # where ARGS are the function's arguments, and PROTO is
        # the *returned function pointer*'s prototype.
        name = "%s(%s)" % (self.name, self.argv)
        decl = mkdeclarator(self.rtype, name)
        if self.body == "":
            outf.write(decl + ";\n")
        else:
            outf.write("%s { %s }\n" % (decl, self.body))

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

    def _generate(self, outf):
        if self.cond != "":
            if self.cond[0] == '?':
                outf.write("#if %s\n" % self.cond[1:])
            else:
                outf.write("#ifdef %s\n" % self.cond)
        outf.write("extern char %s[(%s) ? 1 : -1];\n"
                   % (self.name, self.expr))
        if self.cond != "":
            outf.write("#endif\n")

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

    def generate(self, outf):
        """Emit code for each test item."""
        for item in self.items:
            item.generate(outf)
        outf.write("\n")

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
    def generate(self, outf):
        items = self.items
        enabled = [item.enabled for item in items]
        for item in items:
            item.generate(outf)
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
        # and STANDARD and MODULE are defined in decltests/CATEGORIES.ini.
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

    # WARNING: The next three methods can only be used after generate() has
    # been called at least once.
    def disable_line(self, line):
        """Disable the test case at line LINE (or just before it -- necessary
           for #if(def)-wrapped test cases)."""
        while line > 0 and not self.line_index.has_key(line):
            line -= 1
        assert line > 0
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

    def generate(self, outf):
        """Write the test program to OUTF.
           WARNING: Caller is responsible for emitting an #include of the
           header under test (and all its dependencies) *before* calling
           this function."""

        # If all tests are disabled, and the header under test contains
        # nothing but macros, we could trip over the requirement that a
        # translation unit contain at least one top-level definition or
        # declaration (C99 6.9 -- implicit in the grammar; the
        # "translation-unit" production does not accept an empty token
        # sequence).
        outf.write("int avoid_empty_translation_unit;\n")

        if self.global_decls != "":
            outf.write(self.global_decls)
            outf.write("\n\n")

        # We have to list each category explicitly because they need to
        # happen in a particular order.
        for c in self.types:         c.generate(outf)
        for c in self.fields:        c.generate(outf)
        for c in self.constants:     c.generate(outf)
        for c in self.globals:       c.generate(outf)
        for c in self.special_decls: c.generate(outf)

        # Extra includes are to provide any types that are necessary
        # to formulate function calls: e.g. stdio.h declares functions
        # that take a va_list argument, but doesn't declare va_list
        # itself.  They happen at this point because they can spoil
        # tests for types, fields, constants, and globals.
        if self.extra_includes:
            for h in self.extra_includes:
                outf.write("#include <%s>\n" % h)
            outf.write("\n")

        for c in self.functions: c.generate(outf)
        for c in self.fn_macros: c.generate(outf)
        for c in self.special:   c.generate(outf)

        # Now that we've generated the entire file, construct an index of
        # what's at what line.  This is what enables use of the three
        # methods above (disable_line, all_disabled, disabled_tags).
        self.line_index = {}
        for bloc in self.COMPONENTS.keys():
            for group in getattr(self, bloc):
                for item in group.items:
                    self.line_index[item.lineno] = item

#
# Compilation
#

class Compiler:
    """A Compiler instance knows how to invoke a particular compiler
       on provided source code.  Instantiated from a command + arguments,
       it will identify the compiler and set up to use it.

       Because we are limited to os.system for subprocess invocation,
       and because some compilers require particular environment
       variable settings, it does not work to have more than one
       Compiler instance per process.  Thus, Compiler is also
       responsible for logging and progress reports.

       Uses a config file (defaulting to 'compilers.ini') to track the
       idiosyncracies of various compilers."""

    #@staticmethod
    def prepare_environment(self, ccenv):
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
            if sys.platform == "win32":
                devnull = "nul:"
            else:
                devnull = "/dev/null"
        fd = os.open(devnull, os.O_RDONLY)
        os.dup2(fd, 0)
        os.close(fd)

    def __init__(self, base_cmd, logf, ccenv={}, cfg_fname="compilers.ini"):
        """Identify the compiler that is invoked by BASE_CMD, and initialize
           internal state accordingly."""
        self.base_cmd = base_cmd
        self.logf = logf
        self.error_occurred = 0
        self.need_cr = 0

        self.prepare_environment(ccenv)

        cfg = ConfigParser.ConfigParser()
        cfg.read(cfg_fname)

        (compiler, label) = self.identify(cfg, cfg_fname)
        self.compiler = compiler
        self.label = label

        self.notfound_re = re.compile(cfg.get(compiler, "notfound_re"),
                                      re.VERBOSE)
        self.errloc_re   = re.compile(cfg.get(compiler, "errloc_re"),
                                      re.VERBOSE)

        self.preproc_cmd = cfg.get(compiler, "preproc").split()
        self.preproc_out = cfg.get(compiler, "preproc_out")
        self.compile_cmd = cfg.get(compiler, "compile").split()
        self.compile_out = cfg.get(compiler, "compile_out")

        self.define_opt  = cfg.get(compiler, "define")
        self.conform_opt = cfg.get(compiler, "conform").split()
        self.thread_opt = cfg.get(self.compiler, "threads").split()
        self.test_with_thread_opt = 0

        self.smoke_test(cfg, cfg_fname)
        self.conformance_test(cfg, cfg_fname)

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

    # N.B. logging methods will be moved somewhere else Real Soon Now.

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
        sys.stderr.write(msg)
        sys.stderr.write("..")
        sys.stderr.flush()
        self.need_cr = 1

    def progress_tick(self):
        """Indicate on stderr that forward progress is being made.
           Should normally be paired with one or more calls to log()."""
        sys.stderr.write(".")
        sys.stderr.flush()
        self.need_cr = 1

    def progress_note(self, msg):
        """Indicate status in the middle of an ongoing test.
           MSG is sent both to stderr and to the logfile, and a carriage
           return is forced before and after MSG if necessary."""
        msg = msg.strip()
        self.log(msg)
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
        """Invoke the command in ARGV, capturing all its output and its
           exit code."""
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
    # This is only here till snakebite comes back up and I can test some
    # more wonky vendor compilers.
    #

    def old_compiler_id(self, cc):
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
            (rc, msg) = self.invoke(cmd)

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

    def failure_due_to_nonexistence(self, msg, header):
        """True if MSG contains an error message indicating that HEADER
           does not exist."""
        for m in msg:
            if self.notfound_re.search(m) and m.find(header) != -1:
                return 1
        return 0

    def test_invoke(self, code, action, outname,
                    conform=0, thread=0, opts=[], defines=[]):
        """Invoke the compiler on CODE, in the compilation mode indicated
           by ACTION, CONFORM, THREAD, and OPTS, defining preprocessor
           macros as given by DEFINES.  Return the exit code and the
           error messages, after cleaning up temporary files."""
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
            test_c = named_tmpfile(prefix="cct", suffix="c")
            test_s = self.subst_filename(test_c, outname)
            cmd.extend(self.subst_filename(test_c, action))
            cmd.append(test_c)

            f = open(test_c, "w")
            f.write(code)
            f.write("\n")
            f.close()

            self.progress_tick()
            self.log("compiling:", code.split("\n"))
            return self.invoke(cmd)
        finally:
            delete_if_exists(test_c)
            delete_if_exists(test_s)

    def test_compile(self, code, conform=0, thread=0, opts=[], defines=[]):
        """Convenience function for requesting compilation at least up to
           and including semantic validation."""
        return self.test_invoke(code,
                                self.compile_cmd,
                                self.compile_out,
                                conform, thread, opts, defines)

    def test_preproc(self, code, conform=0, thread=0, opts=[], defines=[]):
        """Convenience function for requesting preprocessing only."""
        return self.test_invoke(code,
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

            self.log("probing compiler identity:", universal_readlines(test1))
            (rc, msg) = self.invoke(self.base_cmd + [test1])
            compiler = parse_output(msg, compilers)

            if compiler == "FAIL":
                self.fatal("unable to parse compiler output.")
            if compiler == "UNKNOWN":
                self.fatal("no configuration available for this "
                           "compiler.  Please add appropriate settings "
                           "to " + repr(cfgf) + ".")

            # Confirm the identification.
            version_argv = cfg.get(compiler, "version").split()
            version_out = cfg.get(compiler, "version_out")

            for arg in version_argv:
                if arg.startswith("$."):
                    test2 = named_tmpfile(prefix="cci", suffix=arg[2:])
                    f = open(test2, "w")
                    f.write("int dummy;\n")
                    f.close()
                    test2_o  = self.subst_filename(test2, version_out)
                    version_argv = self.subst_filename(test2, version_argv)
                    break

            (rc, msg) = self.invoke(self.base_cmd + version_argv)
            if rc != 0:
                self.fatal("detailed version request failed")
            mm = "\n".join(msg[1:]) # throw away the command line
            version_re = re.compile(cfg.get(compiler, "id_regexp"),
                                    re.VERBOSE|re.DOTALL)
            match = version_re.search(mm)
            if not match:
                self.fatal("version information not as expected: "
                           "is this really " + compiler + "?")

            try:
                version = match.group("version")
            except IndexError:
                versio1 = match.group("version1")
                versio2 = match.group("version2")
                if group_matched(versio1): version = versio1
                elif group_matched(versio2): version = versio2
                else:
                    self.fatal("version number not found")

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
        """Perform tests which, if they fail, indicate something horribly
           wrong with the compiler and/or our usage of it (so there is no
           point in continuing with the test run).  Either returns
           successfully, or issues a fatal error."""

        self.begin_test("smoke test")

        test_modes = [
            (self.test_preproc, 0, "preprocess"),
            (self.test_preproc, 1, "preprocess (conformance mode)"),
            (self.test_compile, 0, "compile"),
            (self.test_compile, 1, "compile (conformance mode)")
        ]

        # This code should compile without complaint.
        for (action, conform, tag) in test_modes:
            self.log("smoke test: %s, should succeed" % tag)
            (rc, msg) = action("#include <stdarg.h>\nint dummy;",
                               conform)
            if rc != 0:
                self.fatal("failed to %s simple test program. "
                           "Check configuration for %s in %s."
                           % (tag, self.compiler, cfgf))

        # This code should _not_ compile, in any mode, nor should it
        # preprocess.
        for (action, conform, tag) in test_modes:
            self.log("smoke test: %s, should fail due to nonexistence" % tag)
            (rc, msg) = action("#include <nonexistent.h>\nint dummy;", conform)
            if rc == 0 or not self.failure_due_to_nonexistence(msg,
                                                               "nonexistent.h"):
                self.fatal("failed to detect nonexistence of <nonexistent.h>"
                           " (%s). Check configuration for %s in %s."
                           % (tag, self.compiler, cfgf))

        # We should be able to tell that the error in this code is on line 3.
        for conform in (0,1):
            self.log("smoke test: error on specific line (conform=%d)"
                     % conform)
            (rc, msg) = self.test_compile("int main(void)\n"
                                          "{\n"
                                          "  not_a_type v;\n"
                                          "  return 0;\n"
                                          "}",
                                          conform);
            # The source file will be the last space-separated token on
            # the first line of 'msg'.
            srcf = msg[0].split()[-1]

            for line in msg:
                m = self.errloc_re.search(line)
                if m and m.group("file") == srcf:
                    if int(m.group("line")) == 3:
                        break
                    else:
                        self.fatal("error on unexpected line %s. "
                                   "Check configuration for %s in %s."
                                   % (m.group(line), self.compiler, cfgf))
            else:
                self.fatal("failed to detect error on line 3. "
                           "Check configuration for %s in %s."
                           % (self.compiler, cfgf))

        self.end_test("ok")

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

            self.log("conformance test: trying for %s %s"
                     % (label, expected))
            (rc, msg) = self.test_preproc(testcode, conform=1, opts=opts,
                                          defines=["EXPECTED="+expected])
            if rc == 0:
                return (opts, expected)

            failures.append("")
            failures.extend(msg)

        self.fatal("all %s version tests failed." % label)

    def conformance_test(self, cfg, cfgf):
        """Determine the levels of the C, POSIX, and XSI standards to
           which this compiler + target OS claim to conform; adjust
           'conform_opt' accordingly.  Also figure out whether
           threaded code must be compiled in a special mode."""

        # First find and activate the newest supported C standard.
        self.begin_test("determining ISO C conformance level")
        (opts, result) = self.probe_max_std("C", [
                (cfg.get(self.compiler, "c2011"), "", "201112L"),
                (cfg.get(self.compiler, "c1999"), "", "199901L"),
                # There are two possible values of __STDC_VERSION__ for C1989.
                (cfg.get(self.compiler, "c1989"), "EXPECTED2=1", "199401L")
                ], """\
#if __STDC_VERSION__ != EXPECTED && \\
    (!defined EXPECTED2 || __STDC_VERSION__ != EXPECTED2)
#error "wrong version"
#endif""")
        self.end_test(result)
        self.conform_opt.extend(opts)

        # If we have unistd.h, also find and activate the newest supported
        # POSIX standard.
        self.begin_test("determining POSIX conformance level")
        (rc, msg) = self.test_preproc("#include <unistd.h>\nint dummy;")
        if rc != 0:
            if not self.failure_due_to_nonexistence(msg, "unistd.h"):
                self.fatal("failed to determine presence of <unistd.h>. "
                           "Check configuration for %s in %s."
                           % (self.compiler, cfgf))
            else:
                self.end_test("none")
        else:
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
            # is not worth it.
            (opts, result) = self.probe_max_std("POSIX", [
                    ("", "_XOPEN_SOURCE=700",       "200809L"),
                    ("", "_POSIX_C_SOURCE=200809L", "200809L"),
                    ("", "_XOPEN_SOURCE=600",       "200112L"),
                    ("", "_POSIX_C_SOURCE=200112L", "200112L"),
                    ("", "_XOPEN_SOURCE=500",       "199506L"),
                    ("", "_POSIX_C_SOURCE=199506L", "199506L"),
                ], """\
#include <unistd.h>
#if _POSIX_VERSION != EXPECTED
#error "wrong version"
#endif""")
            self.end_test(result)
            self.conform_opt.extend(opts)

        # Find out whether code that includes <pthread.h> must be
        # compiled in a special mode.  If so, enabling this mode may
        # change dependency sets, so we have to test both ways.
        self.begin_test("checking whether <pthread.h> requires special options")
        (rc, msg) = self.test_compile("#include <pthread.h>\nint dummy;")
        if rc == 0:
            self.end_test("no")
        elif self.failure_due_to_nonexistence(msg, "pthread.h"):
            self.end_test("no (it's absent)")
        else:
            (rc, msg) = self.test_compile("#include <pthread.h>\nint dummy;",
                                          thread=1)
            if rc == 0:
                self.test_with_thread_opt = 1
                self.end_test("yes")
            else:
                self.fatal("pthread.h exists but cannot be compiled? "
                           "Check thread configuration for %s in %s."
                           % (self.compiler, cfgf))

    def report(self, outf):
        """Report the identity of the compiler and how we're going to
           use it."""
        outf.write("old: %s\n" % self.old_compiler_id(self.base_cmd))
        outf.write("new: %s\n" % self.label)
        outf.write("conformance options: %s\n" % " ".join(self.conform_opt))
        outf.write("repeat tests with threads: %d\n"
                   % self.test_with_thread_opt)

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
       the fields of each stanza of errors.ini."""
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
# hit a failure mode that isn't coded into errors.ini yet.
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

    required_modules = None
    def init_required_modules(self):
        self.required_modules = {"": 1}

        parser = ConfigParser.ConfigParser()
        parser.read("decltests/CATEGORIES.ini")
        if parser.has_section("required_modules"):
            for m in parser.options("required_modules"):
                self.required_modules[m] = 1

    def __init__(self, tester):
        self.missing_items = []
        self.wrong_items = []
        self.uncertain_items = []

        if self.required_modules is None:
            self.init_required_modules()

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
                        self.required_modules.has_key(mod)):
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

class SpecialDependency:
    """Used to represent [special] dependencies from prereqs.ini.
       Stubs some Header methods and properties so it can be treated
       like one when convenient."""

    PRESENT = ' '

    def __init__(self, header, text):
        self.name = header
        self.text = text.strip()
        self.presence = self.PRESENT
        self.deplist = [ [ [], [] ], [ [], [] ] ]

    def gen_includes(self, conform, thread, already=None):
        return [self.text]

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

    def __init__(self, name, dataset):
        self.name = name
        self.dataset = dataset

        self.presence  = self.UNKNOWN # can be ABSENT, BUGGY, PRESENT
        self.contents  = self.UNKNOWN # can be PRESENT, INCOMPLETE, CORRECT
        self.depends   = None # None=unknown, 0=no, 1=yes
        self.conflict  = None # None=unknown, 0=no, 1=yes
        self.pref_mode = None # will be set to a 2-tuple by test_depends

        # dependency lists form a 2x2 matrix indexed by [conform][thread].
        # initially all are empty.
        self.deplist = [ [ [], [] ],
                         [ [], [] ] ]

        # conflict lists likewise. The Nones are so output_* can tell the
        # difference between "empty set" and "we never scanned this because
        # cc.test_with_thread_opt=0."
        self.conflist = [ [ [], None ],
                          [ [], None ] ]

        # and error lists likewise, except we may not even get to doing
        # conformance tests.
        self.errlist = [ [ [],   None ],
                         [ None, None ] ]

        # caution is also a 2x2 matrix, but of booleans.
        self.caution = [ [ 0, 0 ],
                         [ 0, 0 ] ]

        self.content_results = None

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def log_tests(self, cc):
        outf = StringIO.StringIO()
        outf.write(" presence: " + self.STATE_LABELS[self.presence] + "\n")
        outf.write(" contents: " + self.STATE_LABELS[self.contents] + "\n")
        outf.write("  depends: " + repr(self.depends) + "\n")
        outf.write("pref_mode: " + repr(self.pref_mode) + "\n")
        outf.write("  caution: [..]=%d [c.]=%d [.t]=%d [ct]=%d\n"
                   % (self.caution[0][0],
                      self.caution[1][0],
                      self.caution[0][1],
                      self.caution[1][1]))

        outf.write(" deplists:\n")
        outf.write("   [..] = %s\n"
                   % " ".join([h.name for h in self.deplist[0][0]]))
        outf.write("   [c.] = %s\n"
                   % " ".join([h.name for h in self.deplist[1][0]]))
        outf.write("   [.t] = %s\n"
                   % " ".join([h.name for h in self.deplist[0][1]]))
        outf.write("   [ct] = %s\n"
                   % " ".join([h.name for h in self.deplist[1][1]]))

        outf.write(" errlists:\n")
        outf.write("   [..] = %s\n"
                   % " ".join([h.name for h in self.errlist[0][0]]))
        if self.errlist[1][0] is not None:
            outf.write("   [c.] = %s\n"
                       % " ".join([h.name for h in self.errlist[1][0]]))
        if self.errlist[0][1] is not None:
            outf.write("   [.t] = %s\n"
                       % " ".join([h.name for h in self.errlist[0][1]]))
        if self.errlist[1][1] is not None:
            outf.write("   [ct] = %s\n"
                       % " ".join([h.name for h in self.errlist[1][1]]))

        if self.content_results is not None:
            outf.write(" contents:\n")
            self.content_results.output(outf)

        cc.log("%s = %s" % (self.name, self.state_label()),
               outf.getvalue().split("\n"))

    def log_conflicts(self, cc):
        msg = [" conflict: " + repr(self.conflict),
               "conflists:",
               "   [..] = " + " ".join([h.name for h in self.conflist[0][0]]),
               "   [c.] = " + " ".join([h.name for h in self.conflist[1][0]])]
        if self.conflist[0][1] is not None:
            msg.append("   [.t] = "
                       + " ".join([h.name for h in self.conflist[0][1]]))
        if self.conflist[1][1] is not None:
            msg.append("   [ct] = "
                       + " ".join([h.name for h in self.conflist[1][1]]))

        cc.log("%s = %s" % (self.name, self.state_label()),
               msg)

    def state_code(self):
        if self.presence != self.PRESENT:
            # unknown/absent/buggy exclude all other indicators.
            return self.presence
        else:
            assert self.depends is not None

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
        self.output_annotations(outf, self.deplist, self.output_one_deplist)
        self.output_annotations(outf, self.conflist, self.output_one_conflist)
        self.output_annotations(outf, self.errlist, self.output_one_errlist)
        if self.content_results is not None:
            self.content_results.output(outf)

    def output_one_deplist(self, outf, lst, tag=""):
        if isinstance(lst[0], SpecialDependency):
            assert len(lst) == 1
            outf.write("  $S%s %s\n" % (tag, lst[0].name))
        else:
            outf.write("  $P%s %s\n" %
                       (tag, " ".join([h.name for h in lst])))

    def output_one_conflist(self, outf, lst, tag=""):
        outf.write("  $C%s %s\n" % (tag, " ".join([h.name for h in lst])))

    def output_one_errlist(self, outf, lst, tag=""):
        outf.write("  $E%s %s\n" % (tag, " ".join([h.name for h in lst])))

    def output_annotations(self, outf, cluster, output_1):

        # always output cluster[0][0] if nonempty
        if cluster[0][0]:
            output_1(outf, cluster[0][0])

        # output other lists only if they are not a subset of
        # the contents of a more generic list
        if not_a_subset(cluster[1][0], cluster[0][0]):
            output_1(outf, cluster[1][0], " [conform]")

        if not_a_subset(cluster[0][1], cluster[0][0]):
            output_1(outf, cluster[0][1], " [thread]")

        if (not_a_subset(cluster[1][1], cluster[0][0]) and
            not_a_subset(cluster[1][1], cluster[1][0])):
            output_1(outf, cluster[1][1], " [conform,thread]")

    def extend_errlist(self, conform, thread, errs):
        if self.errlist[conform][thread] is None:
            self.errlist[conform][thread] = []
        l0 = self.errlist[0][0]
        l1 = self.errlist[conform][thread]

        for e in errs:
            if e.caution:
                self.caution[conform][thread] = 1
                ll = l1
            else:
                # Errors that are not "cautions" are put on the
                # "default" error list regardless of what mode we
                # detected them in (the idea is that this problem
                # is a problem regardless of mode, even if the
                # compiler only catches it with warnings on).
                self.presence = self.BUGGY
                ll = l0

            for x in ll:
                if x.name == e.name:
                    break
            else:
                ll.append(e)

    def record_errors(self, cc, msg, conform, thread, ignore_unknown=0):
        errs = self.dataset.is_known_error(msg, self.name)
        if errs is not None:
            cc.progress_note("*** errors detected: %s"
                             % " ".join([err.name for err in errs]))
            self.extend_errlist(conform, thread, errs)
        else:
            if ignore_unknown: return

            cc.error("unrecognized failure mode for <%s>. "
                     "Please investigate and add an entry to %s."
                     % (self.name, self.dataset.errors_fname))
            self.extend_errlist(0, 0, [UnrecognizedError])

    def record_conflict(self, other, conform, thread):
        self.conflict = 1
        for hh in self.conflist[conform][thread]:
            if hh is other:
                break
        else:
            self.conflist[conform][thread].append(other)

    def gen_includes(self, conform, thread, already=None):
        if self.presence != self.PRESENT: return []
        if already is not None:
            if already.has_key(self.name): return []
            already[self.name] = 1

        rv = []
        for h in self.deplist[conform][thread]:
            rv.extend(h.gen_includes(conform, thread, already))
        rv.append(self.name)
        return rv

    def test(self, cc):
        """Perform all checks on this header in isolation (up to
           dependencies).  This blindly calls itself on other header
           objects, and so must be idempotent.

           Conflict checking is done in a second pass, by the dataset."""

        if self.presence != self.UNKNOWN: return

        # Test dependencies first so the logs are not jumbled.
        for h in self.dataset.deps.get(self.name, []):
            h.test(cc)

        cc.begin_test(self.name)

        self.test_presence(cc)
        self.test_depends(cc)
        self.test_contents(cc)
        self.log_tests(cc)

        cc.end_test(self.state_label().lower())

    def test_presence(self, cc):
        if self.presence != self.UNKNOWN: return

        cc.log("testing presence of %s" % self.name)
        (rc, msg) = cc.test_preproc("#include <%s>" % self.name)
        if rc == 0:
            self.presence = self.PRESENT
            return
        if cc.failure_due_to_nonexistence(msg, self.name):
            self.presence = self.ABSENT
            return

        # caution vs error is ignored at this point; all failures are
        # treated as catastrophic.
        self.record_errors(cc, msg, conform=0, thread=0)
        self.presence = self.BUGGY

    def test_depends_1(self, cc, possible_deps, conform, thread):
        failures = []

        # dependency_combs is guaranteed to produce an empty set as the first
        # item in its returned list, and the complete set as the last item.
        for candidate_set in dependency_combs(possible_deps):
            cc.log("dependency test %s mode %s candidates: [%s]" %
                   (self.name, ct(conform, thread),
                    " ".join([h.name for h in candidate_set])))

            depends = []
            already = {}
            for h in candidate_set:
                depends.extend(h.gen_includes(conform, thread, already))
            # handling of specials
            includes = []
            for item in depends:
                if item.startswith("/*"):
                    includes.append(item)
                else:
                    includes.append("#include <%s>" % item)

            # As a sanity check, confirm that this header can be
            # included twice in a row.  Failures of this check are
            # rare and handled via errors.ini.
            includes.append("#include <%s>\n" % self.name)
            includes.append("int avoid_empty_translation_unit;")

            (rc, msg) = cc.test_compile("\n".join(includes),
                                        conform=conform,
                                        thread=thread)
            if rc == 0:
                self.deplist[conform][thread] = candidate_set
                return

            if len(failures) > 0: failures.append("")
            failures.extend(msg)

        # If we get here, there is a serious problem.
        # Look for a known bug in the last set of messages, which will be
        # the maximal dependency set and therefore the least likely to have
        # problems.
        self.record_errors(cc, msg, conform, thread)

    def test_depends(self, cc):
        if self.depends is not None: return
        if self.presence != self.PRESENT: return

        possible_deps = []
        for h in self.dataset.deps.get(self.name, []):
            h.test(cc)
            if h.presence == h.PRESENT:
                possible_deps.append(h)

        self.test_depends_1(cc, possible_deps, 0, 0)
        if self.presence == self.BUGGY: return
        self.test_depends_1(cc, possible_deps, 1, 0)
        if self.presence == self.BUGGY: return
        if cc.test_with_thread_opt:
            self.test_depends_1(cc, possible_deps, 0, 1)
            if self.presence == self.BUGGY: return
            self.test_depends_1(cc, possible_deps, 1, 1)
            if self.presence == self.BUGGY: return
        else:
            self.deplist[0][1] = self.deplist[0][0][:]
            self.deplist[1][1] = self.deplist[1][0][:]

            self.caution[0][1] = self.caution[0][0]
            self.caution[1][1] = self.caution[1][0]

        self.depends = (len(self.deplist[0][0]) > 0 or
                        len(self.deplist[0][1]) > 0 or
                        len(self.deplist[1][0]) > 0 or
                        len(self.deplist[1][1]) > 0)

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

    def test_contents(self, cc):
        if self.presence != self.PRESENT: return
        if self.contents != self.UNKNOWN: return

        if not self.dataset.decltests.has_key(self.name):
            cc.log("no contents test available for %s" % self.name)
            self.contents = self.PRESENT
            return

        tester = self.dataset.decltests[self.name]

        # Contents tests are done only in the preferred mode.
        (conform, thread) = self.pref_mode
        cc.log("contents test for %s in mode %s" %
               (self.name, ct(conform, thread)))

        buf = LineCounter(StringIO.StringIO())
        for item in self.gen_includes(conform, thread, {}):
            if item.startswith("/*"):
                buf.write(item)
                buf.write("\n")
            else:
                buf.write("#include <%s>\n" % item)
        tester.generate(buf)
        (rc, base_msg) = cc.test_compile(buf.getvalue(),
                                         conform=conform, thread=thread)
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
                cc.error("unrecognized failure mode for <%s> (contents tests)."
                         % self.name)
                self.extend_errlist(0, 0, [UnrecognizedError])
                return

            # Record any known errors (for instance, a macro might
            # trigger the infamous legacy_type_decls).  Do not record
            # unknown errors; they are probably from the test code,
            # not the header.
            self.record_errors(cc, msg, conform, thread, ignore_unknown=1)

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
                    tag = tester.disable_line(int(m.group("line")))
                    if tag:
                        cc.log("disabled %s" % tag)

            disabled_tags = tester.disabled_tags()
            if disabled_tags == prev_disabled_tags:
                # Nothing changed, so the compiler is complaining about
                # something we don't know how to turn off.
                cc.error("unrecognized failure mode for <%s> (contents tests)."
                         % self.name)
            prev_disabled_tags = disabled_tags

            buf = LineCounter(StringIO.StringIO())
            for item in self.gen_includes(conform, thread, {}):
                if item.startswith("/*"):
                    buf.write(item)
                    buf.write("\n")
                else:
                    buf.write("#include <%s>\n" % item)
            tester.generate(buf)
            cc.log("retry contents test for %s (mode %s)" %
                   (self.name, ct(conform, thread)))
            (rc, msg) = cc.test_compile(buf.getvalue(),
                                        conform=conform, thread=thread)

        # If we get here, we just had a successful compilation with at
        # least some items disabled.  Annotate accordingly.
        result = ContentTestResult(tester)
        if result.badness == 0:
            # Only optional items failed the tests.
            self.contents = self.INCOMPLETE
        elif result.badness == 1:
            # Some required items failed the tests.
            self.contents = self.INCOMPLETE
            self.caution[conform][thread] = 2
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

    def __init__(self, headers, conform, thread):
        self.debug = 0
        self.conform = conform
        self.thread = thread
        self.header_object = {}
        self.matrix = {}
        self.rdeps = {}
        for h in headers:
            self.header_object[h.name] = h
            self.matrix[h.name] = {}
            self.rdeps[h.name] = []
            for hh in headers:
                self.matrix[h.name][hh.name] = int(hh is h)
        # This has to be done in a second pass so the table is
        # fully constructed.
        for h in headers:
            self.note_dependencies(h, h)

        self.all_headers = sorthdr(self.header_object.keys())

    def note_dependencies(self, baseh, h):
        for hh in h.deplist[self.conform][self.thread]:
            if isinstance(hh, SpecialDependency): continue
            # Record baseh as depending on hh (perhaps transitively).
            # If hh conflicts with X, all the headers it depends on
            # will also be considered to conflict with X.  This is
            # necessary for correctness -- otherwise we can miss
            # certain asymmetric conflicts.
            self.rdeps[hh.name].append(baseh.name)

            # It is impossible to include baseh before hh, and it is
            # mandatory to include hh before baseh.  Therefore there
            # is no point testing either way.  Do not mark the
            # impossible direction as a conflict, because that would
            # be an asymmetric 2 and the assertions below might get
            # confused.
            self.matrix[baseh.name][hh.name] = 1
            self.matrix[hh.name][baseh.name] = 1
            # Consider transitive dependencies also.
            self.note_dependencies(baseh, hh)

    def log_matrix(self, cc, msg):
        if not self.debug:
            cc.log(msg)
            return
        # U+00A0 NO-BREAK SPACE, U+2592 MEDIUM SHADE, U+2588 FULL BLOCK
        codes = [ "\xc2\xa0", "\xe2\x96\x92", "\xe2\x96\x88" ]
        lines = []
        for r in self.all_headers:
            lines.append("".join([codes[self.matrix[r][c]]
                                  for c in self.all_headers]))
        cc.log(msg, lines)

    def check_completely_done(self, cc):
        # Determine whether we are completely done with any headers.
        # If we are, remove them from the set of headers still of
        # interest (but not the conflict matrix).
        headers = self.header_object.keys()
        for x in headers:
            for y in headers:
                if self.matrix[x][y] == 0 or self.matrix[y][x] == 0:
                    break
            else:
                cc.log("conflict test: done with %s" % x)
                if self.header_object[x].conflict is None:
                    self.header_object[x].conflict = 0
                del self.header_object[x]

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
        self.log_matrix(cc, "conflict trial fail")

        xx = self.header_object[x]
        yy = self.header_object[y]
        xx.record_conflict(yy, self.conform, self.thread)
        yy.record_conflict(xx, self.conform, self.thread)
        cc.progress_note("*** conflict identified: %s with %s"
                         % (x, y))

    def record_ok(self, cc, tested):
        # For each header in the tested set, mark every header after
        # that header as ok after that header.
        for i in range(len(tested)):
            x = tested[i]
            if x.startswith("/*"): continue
            for j in range(i+1, len(tested)):
                y = tested[j]
                if y.startswith("/*"): continue

                if self.matrix[x][y] == 2 or self.matrix[y][x] == 2:
                    cc.error("attempting to mark %s with %s as ok when "
                             "already determined to conflict" % (x, y))
                else:
                    self.matrix[x][y] = 1
        self.log_matrix(cc, "conflict trial ok")

    def test_conflict_set(self, cc, cand):
        cc.log("conflict candidate set: %s" % " ".join(cand))
        tset = []
        for i in range(len(cand)):
            # Pass specials through.
            if cand[i].startswith("/*"):
                tset.append(cand[i])
                continue

            # If there is a known conflict of cand[i] with
            # cand[j] for any j < i, discard cand[i].
            for j in range(i):
                if cand[j].startswith("/*"):
                    continue
                if self.matrix[cand[j]][cand[i]] == 2:
                    break
            else:
                tset.append(cand[i])
        if len(tset) < 2:
            return (1, tset)

        cc.log("conflict trial set: %s" % " ".join(tset))

        eset = []
        already = {}
        for h in tset:
            if self.header_object.has_key(h):
                eset.extend(self.header_object[h]
                            .gen_includes(self.conform, self.thread, already))

        cc.log("conflict extended set: %s" % " ".join(eset))

        # handling of specials
        includes = []
        for item in eset:
            if item.startswith("/*"):
                includes.append(item)
            else:
                includes.append("#include <%s>" % item)
        includes.append("int avoid_empty_translation_unit;")

        (rc, msg) = cc.test_compile("\n".join(includes),
                                    conform=self.conform,
                                    thread=self.thread)
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
                    cc.log("conflict trial fail")
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
                    cc.log("conflict trial fail")
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
        candidates = sorthdr(self.header_object.keys())
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
                hd = cand[0]
                tl = cand[-1]
                ncand = []
                for c in cand:
                    if not (self.matrix[hd][c] and self.matrix[c][tl]):
                        ncand.append(c)
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
            if len(self.header_object) < 2:
                return None # done

            # If we get here it is likely that only a few horizontal or
            # vertical stripes of the conflict matrix remain to be filled
            # in.  The most efficient way to do so is to find the header
            # with the most gaps remaining in its row/column and queue
            # it along with all of the gaps.  We need only consider the
            # headers that have not been removed from header_object by
            # check_completely_done.

            headers = self.header_object.keys()
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

                cc.log("conflict test: %s: todo before %d after %d"
                       % (x, colg, rowg))
                if rowg > row_maxg:
                    row_maxg = rowg
                    row_argmg = x
                if colg > col_maxg:
                    col_maxg = colg
                    col_argmg = x

            if row_argmg is not None:
                row = []
                for x in headers:
                    if not self.matrix[x][row_argmg]: row.append(x)
                row.append(row_argmg)
                queue.append(row)

            if col_argmg is not None:
                col = [col_argmg]
                for x in headers:
                    if not self.matrix[col_argmg][x]: col.append(x)
                queue.append(col)

class Dataset:
    """A Dataset instance represents the totality of information known
       about header files on this platform.  It is primarily a dictionary
       of { filename : Header instance } mappings, but also stores shared
       configuration data and some utility methods."""

    def __init__(self):
        self.headers = {}
        self.deplist_fname = "prereqs.ini"
        self.errors_fname = "errors.ini"
        self.decltests_dname = "decltests"
        self.load_deplist(self.deplist_fname)
        self.load_errors(self.errors_fname)
        self.load_decltests(self.decltests_dname)

    def get_header(self, name):
        if self.headers.has_key(name):
            return self.headers[name]
        h = Header(name, self)
        self.headers[name] = h
        return h

    def load_deplist(self, fname):
        cfg = ConfigParser.ConfigParser()
        cfg.read(fname)
        deps = {}
        for h in cfg.options("prerequisites"):
            deps[h] = [self.get_header(p)
                       for p in cfg.get("prerequisites", h).split()]

        for h in cfg.options("special"):
            if deps.has_key(h):
                raise RuntimeError("%s: %s appears in both [prerequisites] "
                                   "and [special]" % (fname, h))
            deps[h] = [SpecialDependency(h, cfg.get("special", h))]

        self.deps = deps

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

    def load_decltests(self, dname):
        decltests = {}
        for f in glob.glob(os.path.join(dname, "*.ini")):
            if f.endswith("CATEGORIES.ini"): continue
            dt = TestProgram(f)
            if decltests.has_key(dt.header):
                sys.stderr.write("%s: skipping extra test for %s\n"
                                 % (f, dt.header))
            decltests[dt.header] = dt
        self.decltests = decltests

    def is_known_error(self, msg, header):
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

    def test_conflicts(self, cc):
        """Conflict testing is done _en masse_ after all available
           headers have been identified, for two reasons.  First, on
           some systems conflicts between two headers are only evident
           (provoke a compiler error) in one of the two possible #include
           orders.  Second, conflict testing is more expensive than all the
           rest of the tests put together.  We have gone to considerable
           algorithmic effort to minimize the number of compiler invocations
           required, and the algorithm is most efficient when operating on
           large batches of headers (assuming conflicts are rare)."""

        self.test_conflict_mode(cc, conform=0, thread=0)
        self.test_conflict_mode(cc, conform=1, thread=0)
        if cc.test_with_thread_opt:
            self.test_conflict_mode(cc, conform=0, thread=1)
            self.test_conflict_mode(cc, conform=1, thread=1)

        for h in sorthdr(self.headers.keys()):
            self.headers[h].log_conflicts(cc)

    def test_conflict_mode(self, cc, conform, thread):

        cc.begin_test("conflict test mode " + ct(conform, thread))

        # Construct a conflict matrix for every known header which is
        # compatible with this compilation mode.
        headers = []
        for h in self.headers.values():
            if h.presence != h.PRESENT: continue
            if h.caution[conform][thread] == 1: continue
            assert h.depends is not None
            headers.append(h)

        matrix = ConflictMatrix(headers, conform, thread)
        matrix.find_conflicts(cc)

        cc.end_test("done")

if __name__ == '__main__':
    def usage(argv):
        raise SystemExit("usage: %s (compiler_id|header.h...) "
                         "[-- cc [ccargs...]]"
                         % argv[0])

    def main(argv, stdout):
        if len(argv) < 2: usage()

        logf = open("st.log", "w")

        if argv[1] == "compiler_id":
            if len(argv) == 2:
                cc = Compiler(["cc"], logf)
            elif argv[2] == "--":
                cc = Compiler(argv[3:], logf)
            else:
                cc = Compiler(argv[2:], logf)
            cc.report(stdout)
        else:
            headers = None
            for i in range(len(argv)):
                if argv[i] == "--":
                    if i == 1 or i == len(argv)-1:
                        usage()
                    headers = argv[1:i]
                    cc = Compiler(argv[i+1:], logf)
                    break
            if headers == None:
                headers = argv[1:]
                cc = Compiler(["cc"], logf)

            dataset = Dataset()
            for h in headers:
                hh = dataset.get_header(h)
                hh.test(cc)

            if cc.error_occurred:
                raise SystemExit(1)

            dataset.test_conflicts(cc)

            if cc.error_occurred:
                raise SystemExit(1)

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
