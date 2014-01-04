Survey of Commonly Available C Header Files
===========================================

Many C programs’ build harnesses are unnecessarily cautious in
checking whether various system headers are available, and/or retain
checks for headers that passed into obsolescence more than a decade
ago.  This report catalogues all the common, non-system-specific, C
system header files available on widely used operating systems, with
notes on common problems and usage requirements. For headers specified
by ISO C and POSIX.1, we also report on how well the *contents* of the
files measure up to the specification.

We are still looking to expand our coverage, but at this stage we can
draw some high-level conclusions:

* Except perhaps in deeply-embedded environments, all of C89’s
  library is universally available.
* Code not intended to run on Windows can also assume most of C99 and
  much of POSIX.  The less-ubiquitous headers from these categories
  are also the less-useful headers.
* Code that *is* intended to run on Windows should only use C89
  headers and :file:`stdint.h`.  If MSVC 2008 support is required, not
  even :file:`stdint.h` can be used.  (Windows compilers do provide a
  small handful of POSIX headers, but they do not contain the
  expected set of declarations!)
* Many different Unix variants ship a similar set of nonstandard
  headers.  We don’t yet know whether the *contents* of these headers
  are reliable cross-platform.

Contents
--------

.. toctree::
   :maxdepth: 2

   results
   survey
   config-ref
   content-tests

.. Indices and tables
.. ==================
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

Credits
-------

Thanks to
Russ Allbery,
David Corry,
Ralf Corsepius,
Jason Curl,
Paul Eggert,
Trent Nelson,
Tim Rice,
Ed Schouten,
and
Keith Thompson
for helpful suggestions and contributions.

License
-------

Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0.
There is NO WARRANTY.
