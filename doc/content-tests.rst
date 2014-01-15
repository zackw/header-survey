Writing Content Tests
=====================

A :dfn:`content test` checks that a particular header declares
everything it's supposed to declare.  Content tests, like
configuration files, are in the INI format described under
:ref:`config-file-syntax`.

We would welcome assistance making the content tests more
comprehensive.  We currently have content tests for all headers
standardized by ISO C and/or POSIX.1, and we believe they accurately
reflect the requirements of the most recent versions of these
standards.  They are less faithful to older standards.  Most
importantly, at present there is no way to indicate that a symbol was
part of version N's requirements but removed from version N+1, so
those symbols are omitted altogether; unfortunately, some of the
affected symbols are quite widely used even now.  Also, as you go back
in time it becomes more and more difficult to find authoritative
information about what was in a particular revision of a standard; our
tests for C1989 in particular are based on triangulation of derivative
documents, not the official standard, and may have significant errors.

We lack content tests for the large repertoire of headers that are
part of the common Unix heritage but have never been standardized;
however, tests for headers marked as "obsolete" in :file:`headers.ini`
are probably not a good use of anyone's time.  We also lack tests for
"unofficial" declarations in standardized headers: for instance, there
is lots of stuff in :file:`netinet/tcp.h` that is at least somewhat
reliable cross-platform, but the only thing POSIX actually requires be
in there is the constant ``TCP_NODELAY``, so at present that is all we
test for.  Our tests for optional language features and bolt-on
modules, such as OpenMP and C TR 18037, could also be improved.

Each header can have at most one file of content tests.  They are
loaded from the :file:`content_tests` subdirectory of the source
repository, and by convention, are named the same as the header they
test, with any slashes replaced by underscores and the trailing ``.h``
replaced with ``.ini``.  (For example, the content tests for
:file:`sys/types.h` are in the file named
:file:`content_tests/sys_types.ini`.)

Here is a simple example which illustrates many of the features of
content tests.

.. highlight:: ini
.. literalinclude:: ../content_tests/stddef.ini

.. extract-doc-comment:: ../content_tests/CATEGORIES.ini

.. picking up where the doc comments in CATEGORIES.ini leave off ..

The :samp:`{symbol-kind}` may be one of the keywords ``types``,
``fields``, ``constants``, ``globals``, ``functions``, ``fn_macros``,
``special_decls``, or ``special``.  Each of these is documented
further below.

:command:`survey-scan` tests the contents of headers by generating C
programs from the content tests, feeding them to the compiler, and
observing the errors, if any.  Thus, many properties in a content test
have values with syntax derived from C syntax.

.. convention:: type declarator

   Many tests of a header's content are fundamentally about confirming
   that a symbol is declared and has the proper type; to do so,
   :command:`survey-scan` sometimes needs to construct *derived* types
   (such as "pointer to T") from the type named in the test file.  The
   official syntax for declaring a C type (an :dfn:`abstract
   declarator` in the language of the C standard) is difficult to
   parse, so types in content tests must be annotated as follows:

   * If you would declare a variable of type :samp:`{T}` by writing
     :samp:`{T} val;` then you can just write :samp:`{T}` in the
     test: ``int``, ``void *``, etc.

   * But if the name of a variable would have to go somewhere in the
     middle of :samp:`{T}`, then you must put a dollar sign where the
     variable name should appear: ``int $[2]``, ``void (*$)(void)``,
     etc.


The Preamble
------------

All content tests must have a ``[preamble]`` section which declares
certain global properties of the test itself.  This section has two
mandatory and three optional properties.

.. prop:: header

   *Required:* The name of the header file (as you would write it in an
   ``#include``) whose contents are tested by this content test.
   (Despite the naming convention described above,
   :command:`survey-scan` does *not* deduce the name of the header to
   test from the filename of a content test.)

.. prop:: baseline

   *Required:* The tag name (from :file:`CATEGORIES.ini`) of the
   oldest / most basic standard which specifies contents for this
   file.  This is used to make a distinction between headers that
   merely don't implement newer standards, and headers that are
   completely noncompliant.

   For instance, many standards since have added declarations to
   :file:`stdlib.h`, but it first appeared in C1989, so its baseline
   is ``c89``.

.. prop:: includes

   *Optional:* The names of any other headers that this header is
   specified to include.  The content tests for those headers will
   also be applied to this header.

   For instance, :file:`inttypes.ini` is specified to include
   :file:`stdint.ini`.

.. prop:: extra_includes

   *Optional:* The names of any additional headers that the generated
   test program must include for the tests to work correctly.  The
   declarations from these headers are only available to tests for
   functions, function-like macros, and special constructs, because
   they can spoil tests for all of the other kinds of declarations.

   For instance, :file:`stdio.h` declares several functions that take
   a ``va_list`` argument, but does not declare ``va_list`` itself;
   to probe for these declarations, the test program must include
   :file:`stdarg.h`.

.. prop:: global

   *Optional:* C source code to place at the top of the generated test
   program, after including the header to test.  This is normally used
   to make global declarations (hence the name) that are necessary for
   a successful test.

   For example, the content test for :file:`stddef.h` uses this
   feature to declare a ``struct`` that it will apply ``offsetof`` to.

Types
-----

The keys of a :samp:`[types:{category}]` section are :dfn:`type names`
(as the C standard uses this term) which should be declared by this
header.  The value associated with each key describes expected
properties of the type:

.. keyval:: {type} = incomplete

    This type is available but may be incomplete, i.e. after including
    the header, one can declare pointers to :samp:`{type}` but not
    necessarily variables of :samp:`{type}` itself.
    Example: ``FILE`` in :file:`stdio.h`.

.. keyval:: {type} = incomplete struct

    As ``incomplete``, but the type name is only available as a
    structure tag, i.e. one must write :samp:`struct {type} *`.
    Example: ``struct timespec`` in :file:`pthread.h`.

.. keyval:: {type} = opaque

    This type is complete but opaque, i.e. one may declare variables
    of type :samp:`{type}`, but cannot necessarily do anything else
    with them.  Example: ``va_list`` in :file:`stdarg.h`.

.. keyval:: {type} = opaque struct

    As ``opaque``, but the type name is only available as a structure
    tag, i.e. one must write :samp:`struct {type}`.  (In existing
    tests, this is actually used when the structure is *not* opaque,
    but we can't be bothered checking for its fields in this context.)

.. keyval:: {type} = signed

    This is a signed integer type.  Example: ``ptrdiff_t`` in :file:`stddef.h`.

.. keyval:: {type} = unsigned

    This is an unsigned integer type.  Example: ``size_t`` in :file:`stddef.h`.

.. keyval:: {type} = integral

    This is an integer type, signedness unspecified.  Example:
    ``wchar_t`` in :file:`stddef.h`.

.. keyval:: {type} = floating

    This is a floating-point type.  Example: ``double_t`` in :file:`math.h`.

.. keyval:: {type} = arithmetic

    This is either an integer or floating-point type, but nothing more
    is specified.  Example: ``clock_t`` in :file:`time.h`.

.. keyval:: {type} = expr({initializer})

    A variable of this type can be initialized with
    :samp:`{initializer}`.  Example: ``bool``, in :file:`stdbool.h`,
    can be initialized to ``true``.


Structure Fields
----------------

The keys of a :samp:`[fields:{category}]` section are fields of a C
``struct`` or ``union`` type which should be accessible after this
header is included.  The value associated with each key may be a
:cvn:`type declarator` in the syntax described above, in which case the
aggregate will be tested for a field of that exact type.  Or, if the
type is not precisely specified in the relevant standard, you may use
the keywords :kv:`integral` or :kv:`arithmetic` instead, with the same
meaning as described above, under `Types`_.

Because INI syntax only allows one level of nesting, it is necessary
to repeat the name of the aggregate on each line.  The name can be
written in one of three forms:

.. keyval:: {aggr}.{field} = {type}

   Use this form if :samp:`aggr` is a valid type name by itself.

.. keyval:: s_{aggr}.{field} = {type}

   Use this form if :samp:`aggr` is a struct tag.

.. keyval:: u_{aggr}.{field} = {type}

   Use this form if :samp:`aggr` is a union tag.

In all cases, :samp:`{field}` may be an identifier or dotted sequence
of identifiers; the latter allows you to test fields of nested structures.

Here is an example, from :file:`signal.ini`, showing the use of the
``s_`` prefix, and a typical case where a :cvn:`type declarator` must be
annotated::

   [fields:x5]
   s_sigaction.sa_handler   = void (*$)(int)
   s_sigaction.sa_sigaction = void (*$)(int, siginfo_t *, void *)
   s_sigaction.sa_mask      = sigset_t
   s_sigaction.sa_flags     = int

   siginfo_t.si_signo = int
   siginfo_t.si_code  = int


Constants
---------

The keys of a :samp:`[constants:{category}]` section are the names of
global constants which should be declared by the header under test.
Constants can be tested in several different ways:

1. If the value is the keyword "``str``", then the constant is
   required to be a macro that expands to a string literal.

2. If the value contains at least one ``$``, it is treated as an
   ``#if`` expression which must be true, with each dollar sign
   replaced by the name of the constant to test. As shorthand, if the
   value does not contain a ``$`` but does begin with one of the C
   relational operators, ``==``, ``!=``, ``<``, ``<=``, ``>``, or
   ``>=``, then it is treated as an ``#if`` expression which must be
   true, with the name of the constant prepended to the value.

3. If the value does not contain any of the above magic strings, then
   it is treated as a :cvn:`type declarator`, and we simply test that the
   named constant can be assigned to a variable of that type. If the
   value is left blank, it defaults to this test, with type ``int``.
   Note that the declarator cannot be one of the forms that requires
   annotation, because ``$`` is reused for expression tests.

4. Tests 2 and 3 can be combined by writing a declarator in square
   brackets, followed by an ``#if`` expression in either of the
   recognized forms.

5. If the *name* of the constant (that is, the key of the key-value
   pair) starts with a dollar sign, then the value is tested verbatim
   as an ``#if`` expression.  This is useful for testing relationships
   among constants.

6. In all of the above cases, the value can be prefixed with
   :samp:`if {condition}:`, which causes the entire test to be wrapped
   in an ``#if`` testing :samp:`{condition}`; i.e. all tests for this
   constant will be skipped if :samp:`{condition}` is false.
   Alternatively, prefixing the test with ``ifdef:`` causes the entire
   test to be wrapped in :samp:`#ifdef {constant-name}`.  This is
   useful for constants which are conditionally present.

Here are some examples.  Testing for ``errno`` constants is very easy::

    EDOM =
    ERANGE =
    EILSEQ =
    # ... many more ...

The tests for :file:`limits.h` use ``:`` instead of ``=`` to mark
values, because of heavy use of relationals at the beginning of the
value.  Most of the features listed above were added for the sake of
this header, which is very complicated.

::

    CHAR_BIT: >= 8
    SCHAR_MAX: [signed char] >= 127
    UCHAR_MAX: [unsigned char] >= 255U
    CHAR_MAX: [char] CHAR_MIN == 0 ? ($ == UCHAR_MAX) : ($ == SCHAR_MAX)

    _POSIX_ARG_MAX: >= 4096
    ARG_MAX: ifdef: >= _POSIX_ARG_MAX

    PAGESIZE: ifdef: >= 1
    PAGE_SIZE: ifdef: >= 1
    $PS_eq_P_S: if defined PAGESIZE && defined PAGE_SIZE: PAGESIZE == PAGE_SIZE

:file:`signal.h` defines constants of a function-pointer type, so the
tests have to work around the unavailability of ``$``-annotated
declarators::

    [preamble]
    header = signal.h
    baseline = c89
    global = typedef void (*sh_type)(int);

    [constants:c89]
    SIG_DFL = sh_type
    SIG_IGN = sh_type
    SIG_ERR = sh_type

    SIGABRT =
    SIGFPE  =
    # ... many more ...


Globals
-------

The keys of a :samp:`[globals:{category}]` section are the names of
global variables which should be declared by the header under test.
The value associated with each key must be a  :cvn:`type declarator`;
the only exception is that if the value is left blank, it defaults to
``int``, as for constants.


Functions
---------

The keys of a :samp:`[functions:{category}]` section are the names of
external functions which should be declared by the header under test.
The value associated with each key is a :dfn:`function specification`,
which is similar to a C function prototype, but reformatted for easier
processing within :command:`survey-scan`.  The general syntax is

    :samp:`{return-type} ":" {argtype} ["," {argtype}]* ["..." {argtype} ["," {argtype}]*]?`

Each :samp:`{type}` is an annotated :cvn:`type declarator`.  If the
function is variadic, indicate this by putting :samp:`...` at the
point where the variable arguments begin.  You have to specify at
least one concrete type after that point, to use in a synthetic
function call; in many cases these will be arbitrary choices.

Here are some examples, from the tests for :file:`stdio.h`::

    [functions:c89]
    remove   = int    : const char *
    rename   = int    : const char *, const char *
    tmpfile  = FILE * : void
    fprintf  = int    : FILE *, const char *, ...const char *, double
    fscanf   = int    : FILE *, const char *, ...char *, double *


Function-like Macros
--------------------

The keys of a :samp:`[fn_macros:{category}]` section are the names of
function-like macros which should be declared by the header under
test. The value syntax is exactly the same as for real functions (see
above); the only difference is in the generated test code, which
cannot (for instance) assume that it should be possible to take a
pointer to a function-like macro.


Special Declarations
--------------------

A :samp:`[special_decls:{category}]` section allows you to test the
ability to make arbitrary file-scope declarations.  This is most
useful for headers that define type specifiers, type qualifiers, or
initializer macros.  Each key in a ``[special_decls]`` section is the
name of a thing to test; unlike all the sections we have described so
far, this key is *not* used in the generated code.  The value
associated with the key is a complete declaration, which will be
emitted nearly verbatim into the generated code.  It must contain
exactly one dollar sign as a placeholder for the declared object name,
and must *not* include a trailing semicolon.

Here are some examples, taken from the tests for :file:`complex.h`::

    [special_decls:c99]
    _Complex = _Complex double $
    complex  =  complex double $

    [special_decls:c2011]
    CMPLX = complex double $ = CMPLX(99, 0)

(``_Complex`` is a C1999 language feature, supposed to be available
even if :file:`complex.h` is not included; ``complex`` is a macro
(expanding to ``_Complex``) defined by :file:`complex.h`.  We test
both so we can distinguish the absence of *compiler* support
for C1999 complex types from a broken :file:`complex.h`.)


Special Constructs
------------------

A :samp:`[special:{category}]` section allows you to test constructs
that can only be used in particular contexts inside the body of a
function.

In the simplest form, each key in a ``[special]`` section is the name
of a thing to test (like ``[special_decls]``, this name is not used in
the generated code). The associated value is the body of a C function
definition, which will be emitted verbatim into the generated code,
with a semicolon tacked on the end.  For instance, testing
:file:`assert.h`::

    [special:c89]
    assert = assert(1 != 0)

By default, the generated function takes no arguments and has no
return value.  You can change this with special keys:

.. keyval:: __args__ = {argument-list}

   Sets the argument list of all the generated functions for the
   current ``[special]`` section to :samp:`{argument-list}`.  Do not
   put parentheses around :samp:`{argument-list}`.

.. keyval:: __rtype__ = {return-type}

   Sets the return type of all the generated functions for the
   current ``[special]`` section to :samp:`{return-type}`.

Content tests run the compiler with aggressive warnings enabled, so it
is important not to have unused, uninitialized, or write-only
variables in the function body; use arguments and a return value
instead.  For instance, testing :file:`iso646.h`::

    [special:c89]
    __args__  = int a, int b
    __rtype__ = int

    and       = return a and b;
    bitand    = return a bitand b;
    # ...

A more complicated form allows you to test two or more things that can
only be used together.

.. keyval:: __body__ = {function-body}

   Use :samp:`{function-body}` as the body of the single test function
   to be generated for this ``[special]`` section.

.. keyval:: __tested__ = {name1} {name2}...

   This ``[special]`` section tests all of the things listed in the
   value, simultaneously.

:kv:`__tested__` and :kv:`__body__` must be used together, and may not
be used in the same ``[special]`` section as the simpler one-item
tests described above.

For instance, ``va_start`` and ``va_end`` must be used together in a
variadic function::

    [special:c89]
    __tested__ = va_start va_arg va_end
    __args__   = int x, ...
    __rtype__  = double
    __body__   =
      int a; double b;
      va_list ap;
      va_start(ap, x);
      a = va_arg(ap, int);
      b = va_arg(ap, double);
      va_end(ap);
      return a + b;


.. .
   Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
   There is NO WARRANTY.
