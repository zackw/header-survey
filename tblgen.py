#! /usr/bin/env python

import errno
import functools
import os
import re
import sys

# hat tip to http://code.activestate.com/recipes/285264-natural-string-sorting/
_natsort_split_re = re.compile(r'(\d+|\D+)')
def natsort_key(s):
    def try_int(s):
        try: return int(s)
        except: return s
    return tuple(try_int(c) for c in _natsort_split_re.findall(s))

@functools.total_ordering
class Group(object):
    def __init__(self, items, label, sequence):
        self.items = items
        self.label = label
        # numbers within labels are sorted numerically
        self.labelkey = natsort_key(label)
        self.sequence = sequence

    @classmethod
    def from_file(cls, fname):
        label = fname
        if fname.startswith("b-") or fname.startswith("h-"):
            label = label[2:]
        if fname.endswith(".txt"):
            label = label[:-4]
        label = label.replace("-", " ")
        sequence = 50

        items = []
        with open(fname, "rU") as fp:
            for line in fp:
                line = line.strip()
                if line == "" or line[0] == "#": continue
                if line[0] == ":":
                    if line.startswith(":label "):
                        label = line[7:]
                    elif line.startswith(":sequence"):
                        sequence = int(line[10:])
                    else:
                        raise RuntimeError("unknown directive-line '{0!r}'"
                                           .format(line))
                    continue

                items.append(line)

        items = frozenset(items)
        return cls(items, label, sequence)

    def __eq__(self, other):
        return (self.sequence == other.sequence and
                self.label == other.label and
                self.items == other.items)

    def __lt__(self, other):
        if self.sequence < other.sequence: return True
        if self.labelkey < other.labelkey: return True
        if self.items < other.items: return True
        return False

    def output_items(self, fp):
        for x in sorted(self.items, key=lambda x: (x.count('/'), x)):
            fp.write(x + '\n')

def U(g1, g2, label, sequence=50):
    return Group(g1.items.union(g2.items), label, sequence)

def I(g1, g2, label, sequence=50):
    return Group(g1.items.intersection(g2.items), label, sequence)

def D(g1, g2, label, sequence=50):
    return Group(g1.items - g2.items, label, sequence)

def load_groups(dirname):
    hgroups = {}
    bgroups = {}
    for fname in os.listdir(dirname):
        if not (fname.startswith("b-") or fname.startswith("h-")):
            continue
        try:
            g = Group.from_file(fname)
        except OSError, e:
            # silently skip directories
            # report all other errors and continue
            if e.errno != errno.EISDIR:
                sys.stderr.write("{}: {}\n".format(e.filename, e.strerror))

        if fname.startswith("b-"):
            bgroups[g.label] = g
        elif fname.startswith("h-"):
            hgroups[g.label] = g

    return hgroups, bgroups

def main():
    h, b = load_groups(".")
    b["ISO C"] = U(b["ISO C90"], b["ISO C99"], "ISO C")
    b["POSIX.1"] = U(b["POSIX.1-1996"], b["POSIX.1-2001 base"], "POSIX.1")
    b["POSIX.1 full"] = U(b["POSIX.1"], b["POSIX.1-2001 optional"],
                          "POSIX.1 full")
    allstd = U(b["ISO C"], b["POSIX.1 full"], "All standard")

    ucom = None
    for k, v in h.iteritems():
        if ("MSVC" in k or "MinGW" in k or "Android" in k):
            continue
        sys.stderr.write(k + " ")
        if ucom is None:
            ucom = v
        else:
            ucom = I(ucom, v, "ucom")
    sys.stderr.write('\n')
    sys.stderr.flush()

    unonstd = D(ucom, allstd, "unonstd")
    unonstd = D(unonstd, b["Obsolete"], "unonstd")
    unonstd.output_items(sys.stdout)

    sys.stdout.write('\n')

    stdnonu = D(allstd, ucom, "stdnonu")
    stdnonu = D(stdnonu, b["Obsolete"], "stdnonu")

    stdnonu.output_items(sys.stdout)

if __name__ == '__main__': main()
