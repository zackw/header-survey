#! /usr/bin/env python

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

def hsorted(hs):
    return sorted(hs, key=hsortkey)

if __name__ == '__main__':
    import sys
    for h in hsorted(sys.stdin.xreadlines()): sys.stdout.write(h)
