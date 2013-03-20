#! /usr/bin/env python

# This program computes the set of headers that scanheaders.py should
# scan for -- that is, header files that you might reasonably expect
# to find on more than one system.  This is computed from the b- and
# r- files given on the command line (or, if there is only one command
# line argument and it's a directory, all the b- and r- files found in
# that directory; or, if there are no command line arguments, all the
# b- and r- files found in the current directory) as follows:
#
# b- files ("baseline") list headers defined by this or that standard.
# We take the union of all b- lists.
#
# r- files ("raw") list headers found in /usr/include on this or that
# operating system.  We take the intersection of all r- lists.
#
# The output is the union of the above two sets.  It should be edited
# into the "common_header_files" list in scanheaders.py, after manual
# validation.

import os
import sys

success = True

def process(fname):
    items = []
    with open(fname, "rU") as f:
        for l in f:
            l = l.strip()
            if l == "" or l[0] == ":" or l[0] == "#": continue
            items.append(l)
    return frozenset(items)

def process_all(files):
    global success
    common = None
    standard = frozenset()
    for fn in files:
        tag = os.path.basename(fn)[:2]
        try:
            cur = process(fn)
        except EnvironmentError, e:
            sys.stderr.write("{}: {}\n".format(e.filename, e.strerror))
            success = False
            continue
        if tag != 'b-' and tag != 'r-':
            sys.stderr.write('{}: unrecognized tag\n'.format(fn))
            success = False
            continue

        if tag == 'b-':
            standard = standard.union(cur)
        else:
            if common is None:
                common = cur
            else:
                common = common.intersection(cur)

    if common is None: return standard
    return standard.union(common)

def scan_dir(dirname):
    global success
    try:
        files = os.listdir(dirname)
    except EnvironmentError, e:
        sys.stderr.write("{}: {}\n".format(e.filename, e.strerror))
        success = False
        return []

    if dirname == ".": complete = lambda f: f
    else:              complete = lambda f: os.path.join(dirname, f)

    return [complete(f)
            for f in files
            if f.startswith("b-") or f.startswith("r-")]

def main(argv):
    if len(argv) == 1:
        files = scan_dir(".")
    elif len(argv) == 2 and os.path.isdir(argv[1]):
        files = scan_dir(argv[1])
    else:
        files = argv[1:]

    if not success: sys.exit(1)
    if len(files) == 0:
        sys.stderr.write("{}: no header lists specified\n".format(argv[0]))
        sys.exit(1)

    headers = process_all(files)
    if not success: sys.exit(1)

    if len(headers) == 0:
        sys.stderr.write("{}: header set is empty\n".format(argv[0]))
        sys.exit(1)

    for h in sorted(headers,
                    key=lambda h: (h.count('/'), h)):
        sys.stdout.write(h + '\n')
    sys.exit(0)

if __name__ == '__main__': main(sys.argv)
