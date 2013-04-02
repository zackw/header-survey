#! /usr/bin/python
# -*- encoding: utf-8 -*-

import cgi
import errno
import os
import re
import sorthdr
import sys

# hat tip to http://code.activestate.com/recipes/285264-natural-string-sorting/
_natsort_split_re = re.compile(r'(\d+|\D+)')
def natsort_key(s):
    def try_int(s):
        try: return int(s)
        except: return s.lower()
    return tuple(try_int(c) for c in _natsort_split_re.findall(s))

class Group(object):
    def __init__(self, items, label, category, sequence):
        self.items = items
        self.label = label
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

        items = []
        with open(fname, "rU") as fp:
            for line in fp:
                line = line.strip()
                if line == "" or line[0] == "#": continue
                if line[0] == ":":
                    if line.startswith(":label "):
                        label = line[7:]
                    elif line.startswith(":category"):
                        category = line[10:]
                    elif line.startswith(":sequence"):
                        sequence = int(line[10:])
                    else:
                        raise RuntimeError("unknown directive-line {0!r}"
                                           .format(line))
                    continue

                items.append(line)

        items = frozenset(items)
        return cls(items, label, category, sequence)

    def __cmp__(self, other):
        return (cmp(self.sequence, other.sequence) or
                cmp(self.catkey, other.catkey) or
                cmp(self.labelkey, other.labelkey) or
                cmp(len(self.items), len(other.items)) or
                cmp(self.items, other.items))

    # delegate item accessors
    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __contains__(self, x):
        return x in self.items


def load_groups(dirname):
    hgroups = []
    bgroups = []
    rv = 0
    try:
        files = os.listdir(dirname)
    except EnvironmentError, e:
        sys.stderr.write("{}: {}\n".format(e.filename, e.strerror))
        rv = 1;
        return rv, hgroups, bgroups

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

        if fname.startswith("b-"):
            bgroups.append(g)
        elif fname.startswith("h-"):
            hgroups.append(g)

    hgroups.sort()
    bgroups.sort()
    return rv, hgroups, bgroups

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

def write_thead(f, hgroups, bgroups):
    f.write("<table><thead>")

    # system-categories row
    f.write("\n<tr><th colspan=\"2\"></th>")
    cat = ""
    span = 0
    for hg in hgroups:
        if cat != hg.category:
            if cat != "":
                f.write("<th class=\"shift\" colspan=\"{}\">"
                        "<span class=\"cl\">{}</span></th>"
                        .format(span, cgi.escape(cat)))
            cat = hg.category
            span = 0
        span += 1
    f.write("<th class=\"shift\" colspan=\"{}\">"
            "<span class=\"cl\">{}</span></th>"
            .format(span, cgi.escape(cat)))

    # systems row
    f.write("</tr>\n<tr><th>Standard</th><th>Header</th>")
    cat = ""
    n = 0
    for hg in hgroups:
        n += 1
        cls = "o" if n%2 else "e"
        if cat != hg.category:
            cls += " cl"
            cat = hg.category
        f.write("<th class=\"skew\"><span class=\"{}\"><span>{}"
                "</span></span></th>"
                .format(cls, cgi.escape(hg.label)))

    f.write("</tr>\n</thead>")

def write_tbody(f, hgroups, bgroups):
    f.write("<tbody>")

    for bg in bgroups:
        first = True
        for h in sorthdr.sorthdr(bg):
            if first:
                f.write("\n<tr><th rowspan=\"{}\" class=\"ct std\">{}</th>"
                        "<th class=\"h ct\">{}</th>"
                        .format(len(bg), cgi.escape(bg.label),
                                cgi.escape(h)))
            else:
                f.write("</th>\n<tr><th class=\"h\">{}</th>"
                        .format(cgi.escape(h)))

            n = 0
            cat = ""
            for hg in hgroups:
                if h in hg:
                    cls = "y"
                    sym = "⚫"
                else:
                    cls = "n"
                    sym = "⚪"

                n += 1
                cls += " o" if n%2 else " e"

                if first: cls += " ct"
                if cat != hg.category:
                    cls += " cl"
                    cat = hg.category

                f.write("<td class=\"{}\">{}</td>".format(cls, sym))

            first = False

    f.write("</tr>\n</tbody></table>")

def write_html(f, hgroups, bgroups):
    write_header(f, "Availability of C header files")
    write_thead(f, hgroups, bgroups)
    write_tbody(f, hgroups, bgroups)
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

    rv, hgroups, bgroups = load_groups(dirname)
    if rv != 0: sys.exit(rv)

    write_html(sys.stdout, hgroups, bgroups)
    sys.exit(0)

if __name__ == '__main__': main()
