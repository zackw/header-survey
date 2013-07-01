#! /usr/bin/env python

# Generate a test program from an .ini file provided as argv[1].
# Program is written to stdout.

import ConfigParser
import StringIO
import os
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

# shared utility routines
def splitto(string, sep, fields):
    """Split STRING at instances of SEP into exactly FIELDS fields."""
    exploded = string.split(sep, fields-1)
    if len(exploded) < fields:
        exploded.extend([""] * (fields - len(exploded)))
    return exploded

squishwhite_re = re.compile(r"\s+")
def squishwhite(s):
    return squishwhite_re.sub(" ", s.strip())

def mkdeclarator(dtype, name):
    # If there is a dollar sign somewhere in dtype, the name goes there
    # (this is mainly for function pointer declarations).  Otherwise it
    # goes at the end.
    ds = splitto(dtype, "$", 2)
    if name == "": # for function prototypes with argument name omitted
        return ds[0] + ds[1]
    elif ds[0][-1] in idchars:
        return ds[0] + " " + name + ds[1]
    else:
        return ds[0] + name + ds[1]

def mk_pointer_to(dtype):
    # Similarly to the above, if there is a dollar sign somewhere in
    # dtype, the star goes right before it; otherwise it goes at the end.
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

class TestItem:
    def __init__(self, infname, std, ann, tag):
        self.infname = infname
        self.std = std
        self.ann = ann
        self.tag = tag
        self.enabled = 1
        self.name = None
        self.lineno = None

    def generate(self, outf):
        if not self.enabled: return
        if self.name is None:
            self.lineno = outf.lineno
            self.name = "t_" + str(self.lineno)
        else:
            if self.lineno < outf.lineno:
                raise RuntimeError("%s (%s:%s): line numbers out of sync "
                                   " (want %d, already at %d)"
                                   % (self.tag, self.std, self.ann,
                                      self.lineno, outf.lineno))
            while outf.lineno < self.lineno:
                outf.write("\n")
        self._generate(outf)

    def _generate(self, outf):
        raise NotImplementedError

idchars = string.letters + string.digits + "_"
class TestDecl(TestItem):
    def __init__(self, infname, std, ann, tag, dtype, init="", cond=""):
        TestItem.__init__(self, infname, std, ann, tag)

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
    def __init__(self, infname, std, ann, tag, rtype="", argv="", body=""):
        TestItem.__init__(self, infname, std, ann, tag)

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
    def __init__(self, infname, std, ann, tag, expr, cond=""):
        TestItem.__init__(self, infname, std, ann, tag)
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
    def __init__(self, infname, std, ann, items):
        self.infname = infname
        self.std = std
        self.ann = ann
        self.preprocess(items)

    def preprocess(self, items):
        raise NotImplementedError

    def pp_special_key(self, k, v, reject_normal=0):
        # currently there are no shared special keys

        # non-special key?
        if len(k) < 2 or k[:2] != "__" or k[-2:] != "__":
            if not reject_normal:
                return 0

        raise RuntimeError("%s [functions:%s:%s]: "
                           "invalid or misused key '%s'"
                           % (self.infname, self.std, self.ann, k))

    def generate(self, outf):
        items = self.items
        keys = items.keys()
        keys.sort()
        for k in keys:
            items[k].generate(outf)
        outf.write("\n")

class TestTypes(TestComponent):
    def preprocess(self, items):
        pitems = {}
        for k,v in items.items():
            if self.pp_special_key(k, v): continue

            k = " ".join(k.split("."))

            if len(v) >= 7 and v[:5] == "expr(" and v[-1] == ")":
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype=k, init=v[5:-1])

            elif v == "opaque":
                # Just test that a local variable of this type can be declared.
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype=k)
            elif v == "opaque struct":
                # Same as "opaque" but tacks "struct" on the beginning of the typename.
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype="struct " + k)
            elif v == "incomplete":
                # Test that a pointer to this type can be declared.
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype=k+" *")
            elif v == "incomplete struct":
                # Writing "struct X *y;" at top level will forward-declare X
                # as a structure tag if it's not already visible.  So will
                # most other declarations containing "struct X" that don't
                # require it to be complete.  Until someone has a better idea,
                # we define a _function_ with "struct X *y" in its argument
                # list, which provokes a warning from both gcc and clang if
                # the tag isn't already visible (it still forward-declares the
                # tag, but with a surprisingly limited scope, so a warning was
                # felt useful).
                pitems[k] = TestFn(self.infname, self.std, self.ann,
                                   tag=k, argv="struct " + k + " *xx")

            # ??? Can we do better about enforcing signed/unsigned/floating/integralness?
            elif v == "signed":
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype=k, init="-1")
            elif v == "unsigned" or v == "integral" or v == "arithmetic":
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype=k, init="1")
            elif v == "floating":
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype=k, init="6.02e23")
            elif v == "scalar":
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype=k, init="0")
            else:
                raise RuntimeError("%s [types:%s:%s]: %s: "
                                   "unimplemented type category %s"
                                   % (self.infname, self.std, self.ann, k, v))
        self.items = pitems

class TestStructs(TestComponent):
    def preprocess(self, items):
        pitems = {}
        for k,v in items.items():
            if self.pp_special_key(k, v): continue

            (typ, field) = splitto(k, ".", 2)
            if field == "":
                raise RuntimeError("%s [structs:%s:%s]: %s: missing field name"
                                   % (self.infname, self.std, self.ann, k))
            # "s_TAG" is shorthand for "struct TAG", as "option" names
            # cannot contain spaces; similarly, "u_TAG" for "union TAG"
            if typ[:2] == "s_": typ = "struct " + typ[2:]
            if typ[:2] == "u_": typ = "union " + typ[2:]

            # There are two tests for each field, because some systems
            # have "harmless" divergences from the precise type
            # specified by the standard.  The more aggressive test is
            # to take a pointer to the field.  The less aggressive
            # test is to set the field to zero, which confirms only
            # that the field does exist (zero is a valid initializer
            # for every scalar type in C).
            #
            # If the declared type is "integral" or "arithmetic"
            # we skip the first test.
            #
            # If the declared type is "O:something", we chop off the
            # O: and skip the second test.  (O is for Opaque, but this
            # should be used for any non-scalar type.)
            #
            # If the declared type ends with [], we adjust the first test
            # to avoid attempting to return an array (which is invalid)
            # and skip the second test.
            argv=mkdeclarator(mk_pointer_to(typ), "xx")
            opaque = 0
            addressop = "&"
            if v.startswith("O:"):
                v = v[2:]
                opaque = 1
            if v.endswith("[]"):
                v = v[:-2]
                opaque = 1
                addressop = ""
            if v != "integral" and v != "arithmetic":
                pitems[k+".1"] = TestFn(self.infname, self.std, self.ann,
                                        tag=k+".1",
                                        rtype=mk_pointer_to(v), argv=argv,
                                        body="return %sxx->%s" % (addressop,
                                                                  field))
            if not opaque:
                pitems[k+".2"] = TestFn(self.infname, self.std, self.ann,
                                        tag=k+".2",
                                        rtype="void", argv=argv,
                                        body="xx->" + field + " = 0")

        self.items = pitems

dollar_re = re.compile(r"\$")
class TestConstants(TestComponent):
    def preprocess(self, items):
        pitems = {}
        for k,v in items.items():
            if self.pp_special_key(k, v): continue

            # Constants may be conditionally defined; notably, X/Open
            # specifies lots of these in limits.h and unistd.h.  To
            # handle this, when the value starts with "ifdef:", we
            # wrap #ifdef NAME ... #endif around the test.  It can
            # also start with "if CONDITION:" which case we wrap #if
            # CONDITION ... #endif around the test.  Note that in the
            # latter case, CONDITION may not contain a colon.
            cond = ""
            if v.startswith("ifdef:"):
                cond = k
                v = v[6:]
            elif v.startswith("if "):
                colon = v.find(":")
                if colon == -1:
                    raise RuntimeError("%s [constants:%s:%s]: %s: "
                                       "ill-formed #if expression"
                                       % (self.infname, self.std, self.ann, k))
                cond = '?'+v[3:colon]
                v = v[(colon+1):]

            # If 'k' starts with a dollar sign, it is not a real
            # constant name; 'v' is an expression to be tested
            # literally.  Otherwise, if 'v' contains dollar signs,
            # each of them is replaced with 'k' (the constant name) to
            # form the expression to test; or if it starts with a
            # relational operator, 'k' is inserted before the
            # operator.
            if k.startswith("$"):
                pitems[k] = TestCondition(self.infname, self.std, self.ann,
                                          tag=k, expr=v, cond=cond)
            elif v.find("$") != -1:
                pitems[k] = TestCondition(self.infname, self.std, self.ann,
                                          tag=k, expr=dollar_re.sub(k, v),
                                          cond=cond)
            elif v.find(">") != -1 or v.find("<") != -1 or v.find("=") != -1:
                pitems[k] = TestCondition(self.infname, self.std, self.ann,
                                          tag=k, expr=k + " " + v,
                                          cond=cond)
            elif v == "str":
                # testing for a string literal
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype="const char $[]",
                                     init = "\"\"" + k + "\"\"",
                                     cond=cond)
            else:
                if v == "": v = "int"
                pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                     tag=k, dtype=v, init=k,
                                     cond=cond)
        self.items = pitems

class TestGlobals(TestComponent):
    def preprocess(self, items):
        pitems = {}
        for k,v in items.items():
            if self.pp_special_key(k, v): continue

            if v == "": v = "int"
            pitems[k] = TestFn(self.infname, self.std, self.ann,
                               tag=k, rtype=v, body="return " + k)
        self.items = pitems


class TestFunctions(TestComponent):
    def preprocess(self, items):
        pitems = {}
        for k, v in items.items():
            if self.pp_special_key(k, v): continue

            (rtype, argtypes, argdecl, call, return_) = crunch_fncall(v)

            # Each function is tested three ways.  The most stringent test is
            # to declare a function pointer with its exact (should-be)
            # prototype and set it equal to the function name.  This will
            # sometimes fail because of acceptable variation between the
            # standard and the system, so we also test that we can call the
            # function passing arguments of the expected types.  That test is
            # done twice, once suppressing any macro definition, once not.
            pitems[k+".1"] = TestDecl(self.infname, self.std, self.ann,
                                      tag=k+".1",
                                      dtype = rtype + " (*$)(" + argtypes + ")",
                                      init = k)
            pitems[k+".2"] = TestFn(self.infname, self.std, self.ann,
                                    tag=k+".2",
                                    rtype = rtype,
                                    argv  = argdecl,
                                    body  = "%s(%s)(%s);" % (return_, k, call))
            pitems[k+".3"] = TestFn(self.infname, self.std, self.ann,
                                    tag=k+".3",
                                    rtype = rtype,
                                    argv  = argdecl,
                                    body  = "%s%s(%s);" % (return_, k, call))
        self.items = pitems

class TestFnMacros(TestComponent):
    def preprocess(self, items):
        pitems = {}
        for k, v in items.items():
            if self.pp_special_key(k, v): continue

            (rtype, argtypes, argdecl, call, return_) = crunch_fncall(v)

            # Function-like macros can only be tested by calling them in
            # the usual way.
            pitems[k] = TestFn(self.infname, self.std, self.ann,
                               tag=k,
                               rtype = rtype,
                               argv  = argdecl,
                               body  = "%s%s(%s);" % (return_, k, call))
        self.items = pitems

class TestSpecial(TestComponent):
    def preprocess(self, items):
        pitems = {}
        argv  = items.get("__args__", "")
        rtype = items.get("__rtype__", "")

        if items.has_key("__tested__"):
            if not items.has_key("__body__"):
                raise RuntimeError("%s [special:%s:%s]: section incomplete"
                                   % (self.infname, self.std, self.ann))
            for k in items.keys():
                if (k != "__args__" and
                    k != "__rtype__" and
                    k != "__tested__" and
                    k != "__body__"):
                    self.pp_special_key(k, items[k], reject_normal=1)

            tag = items["__tested__"]
            body = items["__body__"]
            tfn = TestFn(self.infname, self.std, self.ann,
                         tag, rtype, argv, body)
            for t in tag.split():
                pitems[t] = tfn
        else:
            for k,v in items.items():
                if (k == "__args__" or k == "__rtype__"): continue
                if self.pp_special_key(k, v): continue
                vx = v.split(":", 1)
                if len(vx) == 2:
                    tfn = TestFn(self.infname, self.std, self.ann,
                                 k, vx[0], argv, vx[1])
                else:
                    tfn = TestFn(self.infname, self.std, self.ann,
                                 k, rtype, argv, v)
                pitems[k] = tfn

        self.items = pitems

    def generate(self, outf):
        items = self.items
        keys = items.keys()
        keys.sort()
        # the following dance with 'enabled' is necessary because if
        # __tested__ had more than one entry, a single TestFn object
        # will be in the list more than once
        enabled = [items[k].enabled for k in keys]
        for k in keys:
            items[k].generate(outf)
            items[k].enabled = 0
        for k,e in zip(keys, enabled):
            items[k].enabled = e

# TestSpecialDecls is more-or-less a raw interface to TestDecl, and is
# intended for cases where the name of interest isn't a type or
# constant name (e.g. <stdalign.h>, where the name of interest is a
# type specifier).
class TestSpecialDecls(TestComponent):
    def preprocess(self, items):
        pitems = {}
        for k, v in items.items():
            if self.pp_special_key(k, v): continue

            (dtype, init) = splitto(v, "=", 2)
            pitems[k] = TestDecl(self.infname, self.std, self.ann,
                                 tag=k, dtype=dtype, init=init)

        self.items = pitems

class TestProgram:
    COMPONENTS = {
        "types"     : TestTypes,
        "structs"   : TestStructs,
        "constants" : TestConstants,
        "globals"   : TestGlobals,
        "functions" : TestFunctions,
        "fn_macros" : TestFnMacros,
        "special"   : TestSpecial,
        "special_decls" : TestSpecialDecls,
    }

    def __init__(self, fname):
        self.header = None
        self.baseline = None
        self.global_decls = ""
        self.infname = fname
        self.extra_includes = []
        for k in self.COMPONENTS.keys():
            setattr(self, k, [])

        self.load(fname)

    def load(self, fname):
        # We would like to use RawConfigParser but that wasn't available
        # in 2.0, so instead we always use get() with raw=1.
        spec = ConfigParser.ConfigParser()
        spec.optionxform = lambda x: x # make option names case sensitive
        spec.read(fname)

        for sect in spec.sections():
            what, std, ann = splitto(sect, ":", 3)
            items = {}
            for k in spec.options(sect):
                items[k] = spec.get(sect, k, raw=1)
            if what == "preamble":
                if std != "" or ann != "":
                    raise RuntimeError("%s: [preamble] section cannot be "
                                       "annotated" % fname)
                self.load_preamble(fname, items)
            else:
                getattr(self, what).append(
                    self.COMPONENTS[what](fname, std, ann, items))

    def load_preamble(self, fname, items):
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

    def generate(self, outf):
        self.gen_preamble(outf)

        for c in self.types:     c.generate(outf)
        for c in self.structs:   c.generate(outf)
        for c in self.constants: c.generate(outf)
        for c in self.globals:   c.generate(outf)
        for c in self.special_decls: c.generate(outf)

        # extra includes are to provide any types that are necessary
        # to formulate function calls: e.g. stdio.h declares functions
        # that take a va_list argument, but doesn't declare va_list
        # itself.  they happen at this point because they can spoil
        # tests for types, structs, constants, and globals.
        self.gen_extra_includes(outf)

        for c in self.functions: c.generate(outf)
        for c in self.fn_macros: c.generate(outf)
        for c in self.special:   c.generate(outf)

    def gen_preamble(self, outf):
        # It simplifies matters if we just always request the highest
        # relevant level of _XOPEN_SOURCE.
        outf.write("#define _XOPEN_SOURCE 700\n")
        outf.write("#include <%s>\n\n" % self.header)

        if self.global_decls != "":
            outf.write(self.global_decls)
            outf.write("\n\n")

    def gen_extra_includes(self, outf):
        if len(self.extra_includes) == 0: return
        for h in self.extra_includes:
            outf.write("#include <%s>\n" % h)
        outf.write("\n")


def main():
    if len(sys.argv) == 2:
        TestProgram(sys.argv[1]).generate(LineCounter(sys.stdout))
    elif len(sys.argv) == 3:
        tmp = open(sys.argv[2] + "T", "w")
        TestProgram(sys.argv[1]).generate(LineCounter(tmp))
        tmp.close()
        os.rename(sys.argv[2] + "T", sys.argv[2])
    else:
        raise SystemExit("usage: %s test-spec.ini [test-spec.c]" % sys.argv[0])

if __name__ == "__main__": main()
