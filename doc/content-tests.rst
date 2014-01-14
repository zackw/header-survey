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

.. literalinclude:: ../content_tests/stddef.ini
   :language: ini

Symbol Categorization
---------------------

.. todo:: document :file:`CATEGORIES.ini` here

File Structure
--------------

Content test files are organized into sections.  The special
``[preamble]`` section declares properties of the test itself.  All
the other sections have structured names which indicate both the kind
of declaration being tested, and a categorization of the declaration
by its standard of origin.

.. todo:: finish explaining symbol categorization here

:command:`survey-scan` tests the contents of headers by generating C
programs from the content tests, feeding them to the compiler, and
observing the errors, if any.  Thus, many properties in a content test
have values with syntax derived from C syntax.

.. convention:: declarator

   Many tests of a header's content are fundamentally about confirming
   that a symbol is declared and has the proper type; to do so,
   :command:`survey-scan` sometimes needs to construct *derived* types
   (such as "pointer to T") from the type named in the test file.  The
   official syntax for declaring a C type (an :dfn:`abstract
   declarator` in the language of the C standard) is difficult to
   parse, so types in content tests must be annotated as follows:

   * If you would declare a variable of type :samp:`{T}` by writing
     :samp:`{T} val;`, then you can just write :samp:`{T}` in the
     test: ``int``, ``void *``, etc.

   * But if the name of a variable would have to go somewhere in the
     middle of :samp:`{T}`, then you must put a dollar sign where the
     variable name should appear: ``int $[2]``, ``void (*$)(void)``,
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
type :cvn:`declarator` in the syntax described above, in which case the
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
``s_`` prefix, and a typical case where a type declarator must be
annotated.

.. code-block:: ini

   [fields:x5]
   s_sigaction.sa_handler   = void (*$)(int)
   s_sigaction.sa_sigaction = void (*$)(int, siginfo_t *, void *)
   s_sigaction.sa_mask      = sigset_t
   s_sigaction.sa_flags     = int

   siginfo_t.si_signo = int
   siginfo_t.si_code  = int


Constants
---------

Globals
-------

Functions
---------

Function-like Macros
--------------------

Special Declarations
--------------------

Special Constructs
------------------


.. .
   Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
   There is NO WARRANTY.
