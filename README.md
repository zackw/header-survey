# Survey of Commonly Available C System Header Files

In this repository, we are conducting a survey to determine the set of
commonly available, non-system-specific, C system header files.  We
suspect that a great many C projects are unnecessarily cautious in
checking whether certain headers are available, and/or retain checks
for headers that passed into obsolescence more than a decade ago.  The
results of this survey will be used to improve matters.

## Inventorying Your Operating System

The simplest way to help is to inventory an operating system we don't
already have an `h-` file for.  We are particularly interested in:

 * More BSD variants
 * Alternative C libraries for Linux
 * Embedded operating systems that claim at least partial POSIX
   conformance

but anything goes as long as it's a conforming hosted C89
implementation (that is, as long as it does provide the headers listed
in the file `b-c1989`).  Since we're investigating what can safely be
assumed to exist everywhere, it is most useful to report on older OS
versions, as long as they're still in current use.  Three to five
years back is a decent rule of thumb.

To generate an inventory, clone the repository and run `scansys.py`
like this:

    $ python scansys.py > h-YOUR-OS 2> failures

Please choose a label for YOUR-OS consistent with the `h-` files that
already exist.  If your C compiler is not named '`cc`', you'll need to
tell `scansys.py` its name:

    $ python scansys.py YOUR-COMPILER > h-YOUR-OS 2> failures

Now read through `failures`.  It will contain a list of headers that
were "present but could not be compiled", normally because they
require the programmer to include some other header first.  Add or
update entries in the `prerequisites` dictionary in `scansys.py` as
necessary.  If you need to do something more than just include other
headers, you can define a new `SPECIAL_` tag---look at how we handle
`regexp.h` for hints.  Continue adjusting and rerunning `scansys.py`
until `failures` comes out empty.

Once you have solved all the failures, edit the top three lines of
`h-YOUR-OS`, which will look something like this:

    # YourOS x.y.z YourCPU
    :category unknown
    :label unknown

If Python picked the wrong fields of `uname -a` to put on the first
line, correct it.  Then set a category and label for your OS.  The
label should be the most common way to refer to this version of your
OS, something like "MacOSX 10.6" or "Solaris 11".  In the case of
Linux or other much-reused kernels, it may be more useful to identify
the C library - "GNU libc", "Android", "dietlibc", etc.  The category
should identify a broad class of similar operating systems to which
yours belongs: "Unix", "Windows", "VMS", that sort of thing.  If the
OS is designed for use on special-purpose devices and/or does not
provide what one would think of as a "complete" computing environment,
prepend the word "embedded" to the category.  (For instance, Android
and iOS should both be categorized "embedded Unix".)

Send a pull request for your `h-` file and your changes to `scansys.py`.

## Baseline Lists

If you remember when function definitions looked like

    int foo(bar)
       int bar;
    {

then we'd appreciate your having a look at our baseline lists.  These
are the files named `b-something`, and each defines a set of header
files that's either specified by a particular standard, or by common
convention.  It is the latter that we need help with.  Specifically,
is there anything in `b-obsolete` that belongs in `b-ucom`, or vice
versa?  Is there anything *missing* from `b-ucom` or `b-obsolete`, and
not mentioned in any other b-file?

If you're doing this, you might also want to look at the `r-` files,
which contain raw lists of everything in `/usr/include` on a tiny
sample of bleeding-edge OSes.  Here we are trying to be as inclusive
as possible but still weed out headers that are specific to one OS.
The `b-` and `r-` files feed into `setcommon.py` to generate the big
list in `scansys.py`.

## Table Generation

The end-goal of this project is to generate a nice readable table of
which OSes have which headers, and to highlight the ones that are
ubiquitous.  This is still a work in progress, but if you'd like to
help out with `tblgen.py`, we'd be delighted to have the assistance.

