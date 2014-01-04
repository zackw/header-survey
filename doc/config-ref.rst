Configuration Reference
=======================

File Syntax
-----------

All configuration, content test, and inventory files are in a
particular rescension of the "INI" format recognized by Python's
`ConfigParser`_.  This parser has gone through substantial changes
over the course of the 2.0 release series, so we will be concrete:

* Comments start with a :kbd:`#` in column 1 and extend to the end of
  the line.  :kbd:`#` does *not* introduce a comment if anything
  precedes it on the line (even whitespace).  In some files, comments
  introduced with :kbd:`##` will be copied into this documentation, so
  don't do that unless you mean it.

* Files are divided into sections.  Section headers are lines by
  themselves, reading :samp:`[{section-name}]` (square brackets are
  literal).  There must be at least one section header before the
  first property-value pair.  The section ``[DEFAULT]`` has special
  significance: properties in that section provide :dfn:`default
  values` for all the other sections. (Most files do not have a
  ``[DEFAULT]`` section.)

* Property-value pairs consist of a property name, optional
  whitespace, a colon or equals sign, and then a value, which runs
  until the end of the line.  Values may be empty, but the colon or
  equals sign is mandatory.

* Values can be extended onto multiple lines by prefixing the second
  and subsequent lines of the value with at least one space
  character.  The newlines will be preserved in the parsed value.

* The "interpolation" mechanism described in Python's ConfigParser
  documentation is **not** available.

* Property names can contain ASCII letters, digits, and the
  punctuation characters ``.`` ``,`` ``_`` ``/`` and ``$``.
  Section header names can contain all of the above plus ``:``.

Syntactic Conventions
---------------------

Some property values have syntax of their own.  There are three
such syntaxes that are used often enough to warrant their own
description.

.. convention:: human-readable text

   All values described as "human-readable text" or a "human-readable
   label" will be interpreted as `reStructuredText`_ when generating
   this report and documentation.

.. convention:: regular expression

   All values described as a "regular expression" or "regex" conform
   to the `extended regex syntax supported by Python 2.0`_, which is
   similar to (but not exactly the same as) the syntax popularized by
   Perl.  They are all compiled in ``VERBOSE`` mode, which means:

       Whitespace within the pattern is ignored, except when in a
       character class or preceded by an unescaped backslash, and,
       when a line contains a "``#``" neither in a character class or
       preceded by an unescaped backslash, all characters from the
       leftmost such "``#``" through the end of the line are ignored.

   In some cases, a regex is required to contain capture groups with
   specific names.  The syntax for this is :samp:`(?P< {name} > {pattern} )`.

.. convention:: command-line option(s)

   All values described as "command-line options" or similar (command,
   command with arguments, etc.) can usually be thought of as
   whitespace-separated lists of tokens.  However, in case it is ever
   necessary to pack whitespace inside an argument, these values
   actually obey the shell quoting conventions for the platform on
   which :command:`survey-scan` is being run.  Specifically, on
   Unix-like systems, `shlex.split`_ is used to split up property
   values into argument vectors; on Windows, `CommandLineToArgvW`_ is
   used instead.  (No other shell features are available; only
   quotation.)

Scanner Configuration
---------------------

.. extract-doc-comment:: ../config/runtimes.ini
.. extract-doc-comment:: ../config/compilers.ini
.. extract-doc-comment:: ../config/errors.ini
.. extract-doc-comment:: ../config/prereqs.ini
.. extract-doc-comment:: ../config/headers.ini

.. _ConfigParser: http://docs.python.org/2.7/library/configparser.html
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _extended regex syntax supported by Python 2.0:
      http://docs.python.org/release/2.0/lib/re-syntax.html
.. _shlex.split: http://docs.python.org/2.7/library/shlex.html?highlight=shlex.split#shlex.split
.. _CommandLineToArgvW: http://msdn.microsoft.com/en-us/library/17w5ykft.aspx

.. .
   Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
   There is NO WARRANTY.
