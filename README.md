# Survey of Commonly Available C System Header Files

Many C programs’ build harnesses are unnecessarily cautious in
checking whether various system headers are available, and/or retain
checks for headers that passed into obsolescence more than a decade
ago.  This repository records inventories of all the common,
non-system-specific, C system header files available on widely used
operating systems.

This project is currently under major revision.  You can see results
from an older iteration at <http://hacks.owlfolio.org/header-survey/>,
and we have reasonable confidence in some high-level conclusions:

 * Except perhaps in deeply-embedded environments, all of C89’s
   library is universally available.
 * Code not intended to run on Windows can also assume most of C99 and
   much of POSIX.  The less-ubiquitous headers from these categories
   are also the less-useful headers.
 * Code that *is* intended to run on Windows should only use C89
   headers and `<stdint.h>`.  If MSVC 2008 support is required, not
   even `<stdint.h>` can be used.  (Windows compilers do provide a
   small handful of POSIX headers, but they do not contain the
   expected set of declarations!)

Assistance with the aforementioned major revisions would be
welcome. Please contact <zackw@panix.com> if you are interested in
helping.
