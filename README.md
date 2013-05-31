# Survey of Commonly Available C System Header Files

Many C programs’ build harnesses are unnecessarily cautious in
checking whether various system headers are available, and/or retain
checks for headers that passed into obsolescence more than a decade
ago.  This repository records inventories of all the common,
non-system-specific, C system header files available on widely used
operating systems.

## How To Use This Data

Our results to date are in an easily-perused table at
<http://hacks.owlfolio.org/header-survey/>.  We are still looking to
expand our coverage, but at this stage we can draw some high-level
conclusions:

 * Except perhaps in deeply-embedded environments, all of C89’s
   library is universally available.
 * Code not intended to run on Windows can also assume most of C99 and
   much of POSIX.  The less-ubiquitous headers from these categories
   are also the less-useful headers.
 * Code that *is* intended to run on Windows should only use C89
   headers and `<stdint.h>`.  If MSVC 2008 support is required, not
   even `<stdint.h>` can be used.  (Windows compilers do provide a
   small handful of POSIX headers, but they do not contain the
   expected set of declarations!  The table unfortunately doesn’t
   reflect this yet.)
 * Many different Unix variants ship a similar set of nonstandard
   headers.  We don’t yet know whether the *contents* of these headers
   are reliable cross-platform.
 * We’ve made an effort to filter out the headers that should no longer
   be used at all; they are in their own category at the very bottom
   of the table.

## How You Can Help

The simplest way to help is to inventory an operating system we don’t
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

### Generating an Inventory

To generate an inventory, you need a clone of the repository, a C
compiler, and [Python](http://www.python.org/).  The inventory-taking
script is called `scansys.py` and we have coded it to work with *any*
2.x release of Python (however, we have only actually *tested* it with
2.0, 2.6, and 2.7; if you find that it doesn’t work with some
intermediate version please let us know).

`scansys.py` has a bunch of options, but you probably won’t need most
of them.  The simplest way to run it is with no options at all:

    $ ./scansys.py > data/h-YOUROS-YOURCC

replacing YOUROS and YOURCC with short names for your operating system
and compiler, respectively.  (Look at the existing files to see how we
name things.)  If you do it this way you will then have to check and
correct the automatically-guessed metadata tags in the file header
after you generate it (see below).  It is also possible to set the
metadata tags on the command line, which you may find convenient if
you want to inventory lots of different systems or compilers.

When run with no options, `scansys.py` assumes that the C compiler’s
command line tool is named `cc`.  If this is not correct, give the
proper name as a non-option argument:

    $ ./scansys.py yourcc > data/h-YOUROS-YOURCC

If you need to give special options to the compiler, put them after
its name:

    $ ./scansys.py cc -std=c99 > data/h-YOUROS-YOURCC

If you’ve got more than one C compiler, we’d appreciate your running
`scansys.py` for each of them (writing the output to distinct files);
often a handful of header files are provided by the compiler rather
than the OS, so we need to check whether *all* the compilers for a
particular platform provide them.

### Inventory Metadata

All inventories have four human-readable metainformation tags at the
top of the file.  They all start with a colon, then a keyword, a
space, and the rest of the line is the value.  It’s very important
that you make sure these tags are accurate.

* `:category` identifies a broad class of similar operating systems to
  which yours belongs: “Unix,” “Windows,” “VMS,” that sort of thing.
  If the OS is designed for use on special-purpose devices and/or does
  not provide what one would think of as a “complete” computing
  environment, prepend the word “embedded” to the category.  (For
  instance, Android and iOS should both be categorized “embedded
  Unix.”)  `scansys.py` does not attempt to guess the category.  You
  can either set it on the command line with `-c <category>`, or edit
  the file after it’s generated.

* `:label` is the common name of the OS being scanned.  You can set it
  on the command line with `-l <label>`; if you don’t, it defaults to
  to `uname -s` for the host where `scansys.py` ran, which is usually
  a recognizable name for the OS *kernel*.  For OSes with more than
  one C library in wide use (e.g. Linux, Windows), it may be
  appropriate to name the C library instead or in addition.  If you
  have inventoried a cross compiler, you need to correct the `:label`
  line to identify the *target*.

* `:version` should be the version number of the *C API*.  It can be
  set on the command line with `-v <ver>`.  It defaults to `uname -r`,
  which is, again, the version number of the *kernel*; if there’s more
  than one C library, you probably want its version number instead
  (again, see what we’ve done for Linux and Windows).

* `:compiler` should be the official name and major.minor version
  number of the compiler you used.  It can be set on the command line
  with `-C <compiler>`; it defaults to the command line name of the
  compiler, which is often too generic.

You will see a few other `:`-prefixed tags in the file.  These are for
internal use; you shouldn’t need to mess with them.

Here’s an example inventory header after vetting by a human:

    # host: FreeBSD 8.3-RELEASE-p6
    # cc: gcc (GCC) 4.2.1 20070719  [FreeBSD]
    :sequence 30
    :category Unix
    :label FreeBSD
    :version 8.3
    :compiler GCC 4.2
    :gen 1

### Inventory Errors

The bulk of an inventory file is just a list of all the headers
provided by your operating system.  In addition to vetting the
metadata, you need to check this list for errors.  Look for lines
that start with an exclamation point, `!`.  Headers marked this way
are present on your system, but the test program failed to compile.
The `!`-line will be followed by comment lines listing the error
messages emitted by the compiler.

There are three kinds of correctable problems that we’ve seen:

 * Some headers require the programmer to include some other header
   first.  This is probably what has happened if the error messages
   appear to be talking about missing type definitions.  `scansys.py`
   already knows how to deal with many such headers, but we find new
   ones just about every time we inventory a new OS.  Header files
   marked with a leading `%` are known cases of this problem—you’ll
   notice that those have `$ Requires something.h` immediately
   afterward.  `$` lines are annotations for the header just above, in
   the generated table of results.  They can be marked up with HTML.

   To teach `scansys.py` about new cases of this problem, edit
   `prereqs.ini` and add entries to the `[prerequisites]` section.

 * Some headers require a chunk of code which *isn’t* just some
   `#include`s.  We don’t expect you will find new cases of this
   problem, but if you do, add an entry to the to the `[special]`
   section of `prereqs.ini`.  It should start with a block comment
   explaining the situation, which will become an annotation for that
   header in the generated table.

 * Some headers insist that the compiler be in a particular mode.  For
   instance, `<complex.h>` sometimes issues an error if the compiler
   isn’t in C99 mode.  If you hit one of these cases, redo the
   inventory with appropriate additional command-line options for the
   compiler.  If there is no single command-line setting that will
   make all your system’s headers happy, look for one that makes all
   the non-“obsolete” headers happy (the “obsolete” headers are listed
   in `data/b-obsolete`).  If you still can’t do it, contact us for
   assistance.

Once you have adjusted things as necessary, rerun the inventory using
the `--recheck` option to `scansys.py`:

    $ ./scansys.py --recheck data/h-YOUROS-YOURCC

You don’t have to repeat any of the other settings.  Keep adjusting
`prereqs.ini` and regenerating the inventory until you have solved as
many `!`-marked lines as possible.

It does sometimes happen that a system header is flat-out *buggy*.  If
there is no way you can fix the problem by adding code above the
header or command-line options to the compiler, leave the `!` line as
is and write `$` lines immediately below it explaining the problem.
See `data/h-irix6.5-mipscc` and `data/h-hpux11.23-gcc` for examples.

Send a pull request for your `h-` file and your changes to
`prereqs.ini`.  If you find that you need to modify `scansys.py`
itself, we’re glad to take patches for that too, but we must
reemphasize that it’s meant to work with any version of Python all the
way back to 2.0.

### Other Ways You Can Help

If you remember when function definitions looked like

    int foo(bar)
       int bar;
    {

then we’d appreciate your having a look at our baseline lists.  These
are the files named `data/b-something`, and each defines a set of
header files that’s either specified by a particular standard, or by
common convention.  It is the latter that we need help with.
Specifically, is there anything in `b-obsolete` that belongs in
`b-ucom`, or vice versa?  Is there anything *missing* from `b-ucom` or
`b-obsolete`, and not mentioned in any other b-file?

We are also interested in any kind of improvement you might like to
suggest (or implement) to the generated table.  That’s done by
`tblgen.py`.  So far, nobody working on this project is much of a Web
guru, and it shows (for instance, the table doesn’t quite look right
in Webkit-based browsers as of this writing).  The process of
generation is kind of clunky, involving several manual steps;
ideally we would have no generated files (`s.css`, `s.js`,
`spritesheet.png`) in the source repo, and we could update the table
just by pushing a new dataset to the server, but none of that’s
implemented right now.

The scanning process is already way more complicated than we expected
it would need to be when we started this project, but it could be more
sophisticated still.  Perhaps the most important lacuna is that it
doesn’t check whether any of these headers contain the declarations
they’re supposed to contain.  We’re not wanting to write an entire
POSIX conformance suite, but a minimal check that each header does
declare what the standard says it declares shouldn’t be *that*
hard...right?

## Credits

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

## Licensing

Copyright 2013 Zack Weinberg <zackw@panix.com> and other contributors.  
Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0  
There is NO WARRANTY.
