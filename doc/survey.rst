Taking an Inventory
===================

We welcome contributions of inventories for operating systems we don't
already have.  We are particularly interested in:

 * More BSD variants
 * Embedded operating systems that claim at least partial POSIX
   conformance
 * Alternative C libraries for Linux
 * Alternative C compilers for systems we already have

but we’re happy to take inventories for *anything* as long as it’s
still in active use outside the retrocomputing community.  Since we’re
investigating what can safely be assumed to exist everywhere, it is
most useful to report on slightly-older but still actively-used
releases.  Three to five years back is a decent rule of thumb.

.. todo:: List of OSes and compilers for which surveys already exist, here.

To generate an inventory, you will need Git, Python 2, and an ISO
C1989-compliant C compiler.  It is not necessary for the *library* to
be C1989-compliant, but inventories for such ancient systems are
unlikely to be of much value.

Use Git to clone https://github.com/zackw/header-survey/ onto the
machine you want to inventory.  If you fork it first, you can submit
your new inventory and any necessary configuration changes with a pull
request, but we are equally happy to take submissions by email.

Running :command:`survey-scan`
------------------------------

You take an inventory with :command:`survey-scan`, which is a Python
script found at the top level of the repository.  It has been coded to
work with *any* 2.x release of CPython (however, we have only tested
it ourselves with 2.0, 2.6, and 2.7; please do let us know if it
doesn't work with some intermediate version).

.. todo:: Complete.


Configuration for a New System
------------------------------

:command:`survey-scan`, needs to be able to identify the C compiler
and runtime it is scanning, so that it can invoke the compiler
properly and write appropriate metadata into the generated inventory.
If you are surveying a C compiler or runtime which has never been
surveyed before, you will need to add a description of it to the
configuration files in the :file:`config` subdirectory.

The most common situation is that you are surveying a new *C runtime*,
but not a new compiler.  In that case, only :file:`config/runtimes.ini`
need be modified.

Compiler configuration is much more complicated than runtime
configuration.  If you are surveying a brand new system (that is, both
a new runtime and a new compiler) we recommend you first take an
inventory of the runtime with a compiler that :command:`survey-scan`
already knows how to invoke (e.g. GCC or Clang) and only then write a
configuration for the new compiler.

.. todo:: Complete.

Correcting Inventory Errors
---------------------------

.. todo:: Write section.

.. .
   Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
   There is NO WARRANTY.
