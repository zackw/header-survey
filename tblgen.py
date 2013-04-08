#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import cgi
import errno
import os
import re
import sys

from string import punctuation as _punctuation

# Sort a list of pathnames, ASCII case-insensitively.  All
# one-component pathnames are sorted ahead of all longer pathnames;
# within a group of multicomponent pathnames with the same leading
# component, all two-component pathnames are sorted ahead of all
# longer pathnames; and so on, recursively.

def hsortkey(h):
    def hsortkey_r(hd, *tl):
        if len(tl) == 0: return (0, hd)
        return (1, hd) + hsortkey_r(*tl)

    segs = h.lower().replace("\\", "/").split("/")
    return hsortkey_r(*segs)

def sorthdr(hs):
    return sorted(hs, key=hsortkey)

# hat tip to http://code.activestate.com/recipes/285264-natural-string-sorting/
_natsort_split_re = re.compile(r'(\d+|\D+)')
def natsort_key(s):
    def try_int(s):
        try: return int(s)
        except: return s.lower()
    return tuple(try_int(c) for c in _natsort_split_re.findall(s))

class Group(object):
    def __init__(self, items, label, category, compiler, sequence):
        self.items = items
        self.label = label
        self.compiler = compiler
        self.category = category
        # "embedded X" sorts immediately after X; otherwise,
        # categories are case-insensitive alphabetical
        if category.startswith("embedded "):
            self.catkey = (category[9:].lower(), 1)
        else:
            self.catkey = (category.lower(), 0)
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
        category = "Uncategorized"
        compiler = "unknown"

        items = {}
        with open(fname, "rU") as fp:
            for line in fp:
                line = line.strip()
                if line == "" or line[0] == "#": continue
                if line[0] == ":":
                    if line.startswith(":label "):
                        label = line[7:]
                    elif line.startswith(":category"):
                        category = line[10:]
                    elif line.startswith(":compiler"):
                        compiler = line[10:]
                    elif line.startswith(":sequence"):
                        sequence = int(line[10:])
                    else:
                        raise RuntimeError("{}: unknown directive-line {0!r}"
                                           .format(fname, line))
                    continue

                line = line.replace('\\', '/')
                if line[0] in _punctuation:
                    p = line[0]
                    l = line[1:]
                    if p not in "!@":
                        raise RuntimeError("{}: {}: unsupported tag symbol: {}"
                                           .format(fname, l, p))

                else:
                    p = '.'
                    l = line
                if l in items:
                    raise RuntimeError("{}: duplicate header-line {0!r}"
                                       .format(fname, line))
                items[l] = p

        return cls(items, label, category, compiler, sequence)

    def merge_compiler(self, other):
        for h in self.items:
            if h not in other.items:
                self.items[h] = "@"
        for h in other.items:
            if h not in self.items:
                self.items[h] = "@"

    def __cmp__(self, other):
        return (cmp(self.sequence, other.sequence) or
                cmp(self.catkey, other.catkey) or
                -cmp(len(self.items), len(other.items)) or
                cmp(self.labelkey, other.labelkey) or
                cmp(self.compiler, other.compiler) or
                cmp(self.items, other.items))

    # delegate item accessors
    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __contains__(self, x):
        return x in self.items

    def __getitem__(self, x):
        return self.items[x]

    def get(self, x, d=None):
        return self.items.get(x, d)

def load_groups(dirname):
    groups = []
    rv = 0
    try:
        files = os.listdir(dirname)
    except EnvironmentError, e:
        sys.stderr.write("{}: {}\n".format(e.filename, e.strerror))
        rv = 1;
        return rv, groups

    for fname in os.listdir(dirname):
        if not (fname.startswith("b-") or fname.startswith("h-")):
            continue
        try:
            g = Group.from_file(fname)
        except EnvironmentError, e:
            # silently skip directories
            # report all other errors and continue
            if e.errno != errno.EISDIR:
                sys.stderr.write("{}: {}\n".format(e.filename,
                                                   e.strerror))
                rv = 1

        groups.append(g)
    return rv, groups

def preprocess(groups):
    oses = {}
    stds = []
    for g in groups:
        if g.category == "standard":
            stds.append(g)
        else:
            other = oses.get(g.label)
            if other is not None:
                other.merge_compiler(g)
            else:
                oses[g.label] = g
    stds.sort()
    return sorted(oses.itervalues()), stds

def write_header(f, title):
    title = cgi.escape(title)

    f.write("<!doctype html><html><head><meta charset=\"utf-8\">")
    f.write("<title>{}</title>".format(title))
    f.write("<link rel=\"stylesheet\" href=\"tbl.css\">")
    f.write("</head><body>\n")
    f.write("<h1>{}</h1>\n".format(title))

def write_trailer(f):
    f.write("<script src=\"jquery-1.9.1.min.js\"></script>")
    f.write("<script src=\"jquery.stickytableheaders.js\"></script>")
    f.write("""<script>window.onload=function(){
  $('table').stickyTableHeaders();
}</script>""")
    # deliberate absence of newline at EOF
    f.write("\n</body></html>")

def write_thead(f, oses):
    f.write("<table><thead>")

    # system-categories row
    f.write("\n<tr><th class=\"key\" colspan=\"2\"><span><span>"
            "<span class=\"n\">⚪</span>: absent<br>"
            "<span class=\"y\">⚫</span>: present<br>"
            "<span class=\"cd\">◗</span>: compiler-dependent<br>"
            "<span class=\"bug\">✗</span>: unusably buggy</span></span></th>")
    cat = ""
    span = 0
    for o in oses:
        if cat != o.category:
            if cat != "":
                f.write("<th class=\"shift\" colspan=\"{}\">"
                        "<span class=\"cl\">{}</span></th>"
                        .format(span, cgi.escape(cat)))
            cat = o.category
            span = 0
        span += 1
    f.write("<th class=\"shift\" colspan=\"{}\">"
            "<span class=\"cl\">{}</span></th>"
            .format(span, cgi.escape(cat)))

    # systems row
    f.write("</tr>\n<tr><th>Standard</th><th>Header</th>")
    cat = ""
    n = 0
    for o in oses:
        n += 1
        cls = "o" if n%2 else "e"
        if cat != o.category:
            cls += " cl"
            cat = o.category
        f.write("<th class=\"skew\"><span class=\"{}\"><span>{}"
                "</span></span></th>"
                .format(cls, cgi.escape(o.label)))

    f.write("</tr>\n</thead>")

def write_tbody(f, oses, stds):
    f.write("<tbody>")

    for std in stds:
        first = True
        for h in sorthdr(std):
            if first:
                f.write("\n<tr><th rowspan=\"{}\" class=\"ct std\">{}</th>"
                        "<th class=\"h ct\">{}</th>"
                        .format(len(std), cgi.escape(std.label),
                                cgi.escape(h)))
            else:
                f.write("</th>\n<tr><th class=\"h\">{}</th>"
                        .format(cgi.escape(h)))

            n = 0
            cat = ""
            for o in oses:
                x = o.get(h)
                if x is None:
                    cls = "n"
                    sym = "⚪"
                elif x == ".":
                    cls = "y"
                    sym = "⚫"
                elif x == "@": # compiler dependent
                    cls = "cd"
                    sym = "◗"
                elif x == "!": # buggy
                    cls = "bug"
                    sym = "✗"
                else:
                    raise RuntimeError("{}: {}: unsupported tag symbol: {}"
                                       .format(o.label, h, x))
                n += 1
                cls += " o" if n%2 else " e"

                if first: cls += " ct"
                if cat != o.category:
                    cls += " cl"
                    cat = o.category

                f.write("<td class=\"{}\">{}</td>".format(cls, sym))

            first = False

    f.write("</tr>\n</tbody></table>")

def write_html(f, oses, stds):
    write_header(f, "Cross-platform availability of C header files")
    write_thead(f, oses)
    write_tbody(f, oses, stds)
    write_trailer(f)

def main():
    if len(sys.argv) == 1:
        dirname = "."
    elif (len(sys.argv) == 2
          and sys.argv[1] != "-h" and sys.argv[1] != "--help"):
        dirname = sys.argv[1]
    elif (len(sys.argv) == 3 and sys.argv[1] == "--"):
        dirname = sys.argv[2]
    else:
        sys.stderr.write("usage: " + os.basename(argv[0]) + " directory\n"
                         "Generates a table of header usage from h- and "
                         "b-files found in DIRECTORY.\n"
                         "Table is written to stdout.\n\n")
        if (len(sys.argv) == 2 and (sys.argv[1] == "-h" or
                                    sys.argv[1] == "--help")):
            sys.exit(0)
        else:
            sys.exit(2)

    rv, groups = load_groups(dirname)
    if rv != 0: sys.exit(rv)

    oses, stds = preprocess(groups)
    write_html(sys.stdout, oses, stds)
    sys.exit(0)

if __name__ == '__main__': main()
