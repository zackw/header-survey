# Inventory File Format

Header inventories (the files in [`data/`](data)) are in an ad-hoc
format which started out straightforward but has grown progressively
more cryptic as additional tests were added to
[`scansys.py`](scansys.py).

If you are submitting an inventory, you need to understand the file
format well enough to check it over for problems. It is especially
important that you check the initial block of metadata, which cannot
be wholly machine-generated. Errors elsewhere in the file indicate
bugs in [`scansys.py`](scansys.py), which you should also be on the
lookout for.

## Overall File Structure

Inventory files are line-oriented ASCII text. There are four kinds of
lines, distinguished by the first non-whitespace character on the line:

* Comments begin with a `#` and extend to the end of the line.
  [`scansys.py`](scansys.py) writes comments to inventories sometimes,
  and you are free to add your own. Comments are completely ignored by
  [`tblgen.py`](tblgen.py) and by [`scansys.py`](scansys.py) in
  `--recheck` mode.

  Comments can only be lines of their own; `#` has no special
  significance if it appears anywhere other than as the first
  non-whitespace character on a line.

* Metadata tags record information about the system on which the
  inventory was taken. They are meaningful to both
  [`tblgen.py`](tblgen.py) and [`scansys.py`](scansys.py) in
  `--recheck` mode.

  Metadata lines begin with a `:`, immediately followed by a keyword
  (composed exclusively of lowercase ASCII letters) and one or more
  space characters. The remainder of the line is a value associated
  with the keyword. Some keywords require particular content in their
  value, others allow freeform text.

* Annotations record additional information about the header whose
  inventory line most closely precedes them.

  Annotation lines begin with a `$`, immediately followed by a type
  code (a single uppercase ASCII letter) and one or more spaces. As
  with metadata, the remainder of the line is a value associated with
  the annotation. Unlike metadata, annotation values are always
  codewords of some sort; see below.

* Inventory lines record the state of a particular header.

  They begin with any character other than `#`, `:`, or `$`. If this
  first character is ASCII punctuation it is a state code (see below);
  otherwise the state code is taken to be `' '`. The remainder of the
  line is the name of the header. [`scansys.py`](scansys.py) does not
  put a space between the state code and the name of the header
  (unlike with metadata and annotations).

## Inventory Metadata

Freshly generated inventories have five metadata tags at the top of
the file. It’s very important that you make sure these are accurate.

* `:category` identifies a broad class of similar operating systems to
  which yours belongs: “Unix,” “Windows,” “VMS,” that sort of thing.
  If the OS is designed for use on special-purpose devices and/or does
  not provide what one would think of as a “complete” computing
  environment, prepend the word “embedded” to the category. (For
  instance, Android and iOS should both be categorized “embedded
  Unix.”)  [`scansys.py`](scansys.py) does not attempt to guess the
  category. You can either set it on the command line with `-c
  <category>`, or edit the file after it’s generated.

* `:label` is the common name of the OS being scanned. You can set it
  on the command line with `-l <label>`; if you don’t, it defaults to
  to `uname -s` for the host where [`scansys.py`](scansys.py) ran,
  which is usually a recognizable name for the OS *kernel*. For OSes
  with more than one C library in wide use (e.g. Linux, Windows), it
  may be appropriate to name the C library instead or in addition. If
  you have inventoried a cross compiler, you need to correct the
  `:label` line to identify the *target*.

* `:version` should be the version number of the *C API*. It can be
  set on the command line with `-v <ver>`. It defaults to `uname -r`,
  which is, again, the version number of the *kernel*; if there’s more
  than one C library, you probably want its version number instead
  (again, see what we’ve done for Linux and Windows).

* `:compiler` should be the official name and major.minor version
  number of the compiler you used. It can be set on the command line
  with `-C <compiler>`; it defaults to the command line name of the
  compiler, which is often too generic.

* `:gen` (short for “generation”) is a version number for the
  inventory format itself. [`scansys.py`](scansys.py) sets it
  automatically.  Do not change this line.

In inventories that have been edited by a human, you may also see

* `:sequence` is a number controlling sort order within the generated
  table. You need not adjust or add this.

## Trailing Metadata

[`scansys.py`](scansys.py) writes a few more metadata tags at the
*end* of the file. These are required to make `--recheck` mode work
reliably. They should only be modified if you notice that they contain
pathnames which are specific to your computer (not just to your
operating system).

## Inventory Lines

Inventory lines comprise the bulk of the file.  All inventory lines
begin with a “state code,” which is either blank or a punctuation
character, followed immediately by the name of the header in question.
There is nothing else on an inventory line.

There are presently twelve state codes:

<table>
<tr><th><kbd>?</kbd></th>
<td><b>UNKNOWN</b>: No data for this header. (This code is used
    internally, but should never appear in an inventory on
    disk.)</td></tr>
<tr><th><kbd>-</kbd></th>
<td><b>ABSENT</b>: This header is not available on the inventoried
    system.</td></tr>
<tr><th><kbd>!</kbd></th>
<td><b>BUGGY</b>: This header exists, but has something so severely
    wrong with it that it cannot be used at all, such as provoking a
    compiler error on inclusion, or declaring <i>none</i> of the
    things it is supposed to declare.</td></tr>
<tr><th><kbd>&nbsp;</kbd></th>
<td><b>PRESENT</b>: This header exists and has nothing obviously wrong
    with it, but we have not audited its contents in detail (because
    no one has written a test for its contents).</td></tr>
<tr><th><kbd>%</kbd></th>
<td><b>PRESENT (DEPENDENT)</b>: This header exists.  We have not
    audited its contents in detail.  It requires the programmer to
    include some other header(s) first, but there is nothing else
    wrong with it.</td></tr>
<tr><th><kbd>~</kbd></th>
<td><b>PRESENT (CAUTION)</b>: This header exists.  We have not audited
    its contents in detail, but there is something wrong with it which
    renders it unusable in some (but not all) circumstances.  It may
    also require the programmer to include some other header(s)
    first.</td></tr>
<tr><th><kbd>*</kbd></th>
<td><b>INCOMPLETE</b>: This header has no serious problems, but some
    of the things it is supposed to declare are missing or incorrectly
    declared. (Most contents tests make a distinction between
    <i>required</i> and <i>optional</i> declarations. If a required
    declaration is missing or incorrect, the header will be marked
    <b>INCOMPLETE (CAUTION)</b> instead of just <b>INCOMPLETE</b>; if
    <i>all</i> the required declarations are missing or incorrect, the
    header will be marked <b>BUGGY</b>, even if some optional
    declarations were found.)</td></tr>
<tr><th><kbd>&</kbd></th>
<td><b>INCOMPLETE (DEPENDENT)</b>: This header requires the programmer
    to include some other header(s) first, and does not declare
    everything it is supposed to.</td></tr>
<tr><th><kbd>^</kbd></th>
<td><b>INCOMPLETE (CAUTION)</b>: This header has something wrong with
    it which renders it unusable in some (but not all) circumstances.
    It also fails to declare everything it is supposed to, and it may
    require the programmer to include some other header(s)
    first.</td></tr>
<tr><th><kbd>+</kbd></th>
<td><b>CORRECT</b>: This header exists, has no problems we can detect,
    and declares everything that it is supposed to declare according
    to the most recent applicable standards (normally C and
    POSIX).</td></tr>
<tr><th><kbd>@</kbd></th>
<td><b>CORRECT (DEPENDENT)</b>: This header requires the programmer to
    include some other header(s) first, but it declares everything it
    is supposed to.</td></tr>
<tr><th><kbd>=</kbd></th>
<td><b>CORRECT (CAUTION)</b>: This header has something wrong with it
    which renders it unusable in some (but not all) circumstances, and
    it may require the programmer to include some other header(s)
    first.  However, it does declare everything it’s supposed
    to.</td></tr>
</table>

## Annotations

Annotation lines should appear after every header whose state is not
ABSENT, PRESENT, or CORRECT.  They give details about the problems
encountered with that header.

There are presently seven types of annotation.  Four of them have an
optional `[`<i>mode</i>`]` tag, which appears before any other
information, and indicates that the annotation only applies to a
particular compilation mode.  For instance,

    %netinet/ip6.h
    $P sys/types.h
    $P [conform] sys/types.h sys/socket.h

indicates that `netinet/ip.h` always requires the programmer to
include `sys/types.h` first, and when the compiler is in strict
conformance mode it also requires `sys/socket.h`.

Tests for header contents are done only in the header’s “preferred”
mode (which is a strict conformance mode if possible), so `$M`, `$W`,
and `$X` annotations don't have a mode tag.

* `$P` `[`<i>mode</i>`]` *space-separated list of header names*

  Indicates that in order to include this header, one must first
  include all of the listed headers.  (P is for “prerequisite.”)

  The listed headers may themselves require other headers to be
  included.  [`tblgen.py`](tblgen.py) computes the transitive closure
  for display.

  This annotation should only appear on a header whose state code
  indicates DEPENDENT, CAUTION, or BUGGY.

* `$S` `[`<i>mode</i>`]` *header-name*

  Indicates that in order to include this header, one must first do
  something special.  (S is for “special prerequisite.”)  A
  human-readable explanation of what is required will be found in
  [`prereqs.ini`](prereqs.ini) under the `[special]` entry for
  *header-name*.

  This annotation should only appear on a header whose state code
  indicates DEPENDENT, CAUTION, or BUGGY.

* `$C` `[`<i>mode</i>`]` *space-separated list of header names*

  Indicates that this header cannot be included in the same source
  file as any of the listed headers.  (C is for “conflict.”)

  This annotation should only appear on a header whose state code
  indicates either CAUTION or BUGGY.

* `$E` `[`<i>mode</i>`]` *codeword*

  Indicates that including this header provokes some sort of compiler
  error, possibly only in a particular mode.  (E is for “error.”)  A
  human-readable explanation of the problem will be found in
  [`errors.ini`](errors.ini) under the section heading corresponding
  to the *codeword*.

  This annotation should only appear on a header whose state code
  indicates either CAUTION or BUGGY.

* `$M` `:`<i>category</i>`:` *space-separated list of symbols*

  Indicates that this header fails to declare the symbols in the list.
  (M is for “missing.”)

  The category tag is mandatory, and applies to all the symbols in the
  list; if symbols from multiple categories are missing, there will be
  multiple `$M` lines.  If there is nothing after the category tag,
  that means *none* of the symbols belonging to that category were
  declared.  Category tags are defined and given human-readable names
  in [`decltests/CATEGORIES.ini`](decltests/CATEGORIES.ini).

  This annotation should only appear on a header whose state code
  indicates either INCOMPLETE or BUGGY.

* `$W` `:`<i>category</i>`:` *space-separated list of symbols*

  Indicates that this header does declare the symbols in the list, but
  incorrectly. (W is for “wrong.”)  Category tags work the same way as
  for `$M`.

  This annotation should only appear on a header whose state code
  indicates either INCOMPLETE or BUGGY.

* `$X` `:`<i>category</i>`:` *space-separated list of symbols*

  Indicates that the symbols in the list are either missing or
  incorrect, but we can't tell which.  (X looks kind of like an M and
  a W stacked on top of each other if you squint.) Category tags work
  the same way as for `$M`.

  This annotation should only appear on a header whose state code
  indicates either INCOMPLETE or BUGGY.
