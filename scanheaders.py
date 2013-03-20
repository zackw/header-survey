#! /usr/bin/env python

# This script determines which subset of the following list of "common"
# header files (many are standard, some are not) are present on your
# operating system.  It does not attempt to distinguish between headers
# provided by the "core" operating system and headers provided by add-on
# packages, as this would require detailed understanding of the package
# management facilities.  If you wish, edit headers you know to be provided
# by optional packages out of the results.
#
# Takes one argument, the name of the compiler to use for tests.
# If no argument is provided, defaults to "cc".

import os
import shutil
import subprocess
import sys
import tempfile

common_header_files="""
assert.h
ctype.h
errno.h
float.h
iso646.h
limits.h
locale.h
math.h
setjmp.h
signal.h
stdarg.h
stddef.h
stdio.h
stdlib.h
string.h
time.h
wchar.h
wctype.h
complex.h
fenv.h
inttypes.h
stdbool.h
stdint.h
tgmath.h
sys/types.h
sys/socket.h
dirent.h
fcntl.h
fnmatch.h
glob.h
grp.h
netdb.h
netinet/in.h
netinet/tcp.h
pwd.h
regex.h
sys/mman.h
sys/stat.h
sys/times.h
sys/utsname.h
sys/wait.h
tar.h
termios.h
unistd.h
wordexp.h
noensuch.h
gwibble.h
""".split()

# We detect header files by #including them. On some systems, some header
# files require you to include other headers first.  This is a table of
# all known situations where that's the case.

prerequisites = {
}

def gensrc(wd, header):
    def include(f, h):
        f.write("#include <{}>\n".format(os.path.join(*h.split("/"))))

    src = os.path.join(wd, "htest.c")
    with open(src, "w") as f:
        for p in prerequisites.get(header, []):
            include(f, p)
        include(f, header)
        # End with a global definition, in case some compiler
        # doesn't like source files that define nothing.
        # The #undefs are probably unnecessary, but you never know.
        f.write("#undef int\n#undef main\n#undef void\n#undef return\n"
                "int main(void){return 0;}\n")
    return src

def invoke(wd, argv):
    msg = os.path.join(wd, "htest-out.txt")
    with open(os.devnull, "rb") as stdi:
        with open(msg, "w") as stdo:
            stdo.write("# {}\n".format(" ".join(argv)))
            stdo.flush()
            rc = subprocess.call(argv, stdin=stdi, stdout=stdo,
                                 stderr=subprocess.STDOUT)
            stdo.write("# exit {}\n".format(rc))
    return (rc, msg)

def probe_one(wd, cc, header):
    src = gensrc(wd, header)
    (rc, msg) = invoke(wd, [cc, "-c", src])
    if rc == 0:
        return True
    with open(msg, "rU") as f: errors = f.read()

    (rc, msg) = invoke(wd, [cc, "-E", src])
    if rc == 0:
        sys.stderr.write("# {} present but cannot be compiled:\n"
                         .format(header))
        for e in errors.split("\n"): sys.stderr.write("# {}\n".format(e))

    return False

def probe(compiler, headers):
    wd=None
    good = set(headers)
    try:
        wd = tempfile.mkdtemp()
        src = os.path.join(wd, "htest.c")
        msg = os.path.join(wd, "messages.txt")
        with open(src, "w") as f:
            for h in headers:
                if not probe_one(wd, compiler, h):
                    good.remove(h)
    finally:
        if wd is not None:
            shutil.rmtree(wd)

    return good

if __name__ == '__main__':
    compiler = "cc"
    if len(sys.argv) > 1:
        compiler = sys.argv[1]
    good_headers = probe(compiler, common_header_files)
    for h in sorted(good_headers, key=lambda x: (x.count("/"), x)):
        sys.stdout.write(h + "\n")
