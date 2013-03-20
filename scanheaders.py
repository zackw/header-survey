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
#
# The list is generated by compute-common-headers.py.

import functools
import itertools
import os
import shutil
import subprocess
import sys
import tempfile

import sortheaders

common_header_files="""
a.out.h
aio.h
alloca.h
ar.h
assert.h
complex.h
cpio.h
ctype.h
direct.h
dirent.h
dlfcn.h
elf.h
err.h
errno.h
fcntl.h
fenv.h
float.h
fmtmsg.h
fnmatch.h
fstab.h
fts.h
ftw.h
getopt.h
glob.h
grp.h
iconv.h
ifaddrs.h
inttypes.h
iso646.h
langinfo.h
lastlog.h
libgen.h
limits.h
link.h
locale.h
malloc.h
math.h
memory.h
mntent.h
monetary.h
mqueue.h
ndbm.h
netdb.h
nl_types.h
omp.h
paths.h
poll.h
pthread.h
pwd.h
regex.h
regexp.h
resolv.h
sched.h
search.h
semaphore.h
setjmp.h
sgtty.h
signal.h
spawn.h
stab.h
stdalign.h
stdarg.h
stdatomic.h
stdbool.h
stddef.h
stdfix.h
stdint.h
stdio.h
stdlib.h
stdnoreturn.h
string.h
strings.h
stropts.h
sysexits.h
syslog.h
tar.h
termcap.h
termio.h
termios.h
tgmath.h
thread_db.h
threads.h
time.h
trace.h
uchar.h
ucontext.h
ulimit.h
unistd.h
utime.h
utmp.h
utmpx.h
varargs.h
wchar.h
wctype.h
wordexp.h
arpa/ftp.h
arpa/inet.h
arpa/nameser.h
arpa/nameser_compat.h
arpa/telnet.h
arpa/tftp.h
net/if.h
net/if_arp.h
net/ppp_defs.h
net/route.h
netinet/icmp6.h
netinet/if_ether.h
netinet/igmp.h
netinet/in.h
netinet/in_systm.h
netinet/ip.h
netinet/ip6.h
netinet/ip_icmp.h
netinet/tcp.h
netinet/udp.h
protocols/routed.h
protocols/rwhod.h
protocols/timed.h
rpc/auth.h
rpc/auth_des.h
rpc/auth_unix.h
rpc/clnt.h
rpc/des_crypt.h
rpc/key_prot.h
rpc/pmap_clnt.h
rpc/pmap_prot.h
rpc/pmap_rmt.h
rpc/rpc.h
rpc/rpc_msg.h
rpc/svc.h
rpc/svc_auth.h
rpc/types.h
rpc/xdr.h
rpcsvc/bootparam_prot.h
rpcsvc/mount.h
rpcsvc/nfs_prot.h
rpcsvc/nis.h
rpcsvc/nislib.h
rpcsvc/nlm_prot.h
rpcsvc/rex.h
rpcsvc/rquota.h
rpcsvc/rstat.h
rpcsvc/sm_inter.h
rpcsvc/spray.h
rpcsvc/yp_prot.h
rpcsvc/ypclnt.h
rpcsvc/yppasswd.h
sys/acct.h
sys/dir.h
sys/errno.h
sys/fcntl.h
sys/file.h
sys/ioctl.h
sys/ipc.h
sys/mman.h
sys/mount.h
sys/msg.h
sys/mtio.h
sys/param.h
sys/poll.h
sys/procfs.h
sys/queue.h
sys/reboot.h
sys/resource.h
sys/select.h
sys/sem.h
sys/shm.h
sys/signal.h
sys/socket.h
sys/socketvar.h
sys/stat.h
sys/statfs.h
sys/statvfs.h
sys/syscall.h
sys/syslog.h
sys/termios.h
sys/time.h
sys/timeb.h
sys/times.h
sys/timex.h
sys/types.h
sys/ucontext.h
sys/uio.h
sys/un.h
sys/unistd.h
sys/user.h
sys/utsname.h
sys/wait.h
"""

# We detect header files by including them. On some systems, some header
# files require you to include other headers first.  This is a table of
# all known situations where that's the case.

prerequisites = {
    # from OSX 10.6
    "net/if.h"           : ["sys/socket.h"],
    "netinet/icmp6.h"    : ["netinet/in.h"],
    "netinet/igmp.h"     : ["netinet/in.h"],
    "netinet/ip6.h"      : ["netinet/in.h"],
    "netinet/ip_icmp.h"  : ["netinet/in.h", "netinet/in_systm.h",
                            "netinet/ip.h"],
    "protocols/routed.h" : ["sys/socket.h"],
    "protocols/timed.h"  : ["sys/param.h"],
    "rpc/auth.h"         : ["rpc/rpc.h"],
    "rpc/auth_unix.h"    : ["rpc/rpc.h"],
    "rpc/clnt.h"         : ["rpc/rpc.h"],
    "rpc/pmap_clnt.h"    : ["rpc/rpc.h"],
    "rpc/pmap_prot.h"    : ["rpc/rpc.h"],
    "rpc/pmap_rmt.h"     : ["rpc/rpc.h"],
    "rpc/rpc_msg.h"      : ["rpc/rpc.h"],
    "rpc/svc.h"          : ["rpc/rpc.h"],
    "rpc/svc_auth.h"     : ["rpc/rpc.h"],
    "rpc/xdr.h"          : ["rpc/rpc.h"],
    "rpcsvc/yp_prot.h"   : ["rpc/rpc.h"],
    "sys/acct.h"         : ["sys/types.h"],
    "sys/socketvar.h"    : ["sys/socket.h"],

    # from glibc 2.13
    "rpcsvc/nislib.h"    : ["rpcsvc/nis.h"],
    "regexp.h"           : ["SPECIAL_regexp"],
}

# Some headers are ... special, and require more than just the inclusion
# of other headers.

# The SVID version of the obsolete regexp.h (not to be confused with
# regex.h) has a bunch of embedded, macro-customizable code in it,
# which will not compile unless we provide stubs.
SPECIAL_regexp = r"""
#define INIT
#define GETC() 0
#define PEEKC() 0
#define UNGETC(c) do { } while (0)
#define RETURN(p) return p
#define ERROR(v) return 0
"""

# from http://code.activestate.com/recipes/578272-topological-sort/
def toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. Output is a list of
sets in topological order. The first set consists of items with no
dependences, each subsequent set consists of items that depend upon
items in the preceeding sets.

>>> print '\\n'.join(repr(sorted(x)) for x in toposort({
...     2: set([11]),
...     9: set([11,8]),
...     10: set([11,3]),
...     11: set([7,5]),
...     8: set([7,3]),
...     }) )
[3, 5, 7]
[8, 11]
[2, 9, 10]

"""

    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = \
        functools.reduce(set.union, data.itervalues()) - set(data.iterkeys())
    # Add empty dependences where needed
    for item in extra_items_in_deps:
      data[item] = set()
    while True:
        ordered = set(item for item, dep in data.iteritems() if not dep)
        if not ordered:
            break
        yield ordered
        ndata = {}
        for item, dep in data.iteritems():
           if item not in ordered:
               ndata[item] = dep - ordered
        data = ndata
    if len(data) > 0:
        raise RuntimeError("Cyclic dependencies exist among these items:\n"
                           + "\n".join(repr(x) for x in data.iteritems()))

# Topologically sort the common-headers list according to the prerequisites
# list, so that gensrc() can safely check whether probable-prerequisite
# headers are known to exist, and include them only if so.
def sorted_common_headers():
    topo_in = {}
    for h in common_header_files.split():
        topo_in[h] = set(prerequisites.get(h, []))
    return list(itertools.chain.from_iterable(toposort(topo_in)))

def gensrc(wd, header, known_headers):
    def include(f, h):
        f.write("#include <{0}>\n".format(os.path.join(*h.split("/"))))

    src = os.path.join(wd, "htest.c")
    with open(src, "w") as f:
        for p in prerequisites.get(header, []):
            if p.startswith("SPECIAL_") and not p.endswith(".h"):
                f.write(globals()[p])
            elif p in known_headers:
                include(f, p)
        include(f, header)
        # End with a global definition, in case some compiler
        # doesn't like source files that define nothing.
        # The #undefs are probably unnecessary, but you never know.
        f.write("#undef int\n#undef main\n#undef void\n#undef return\n"
                "int main(void){return 0;}\n")
    return src

def invoke(wd, devnull, argv):
    msg = os.path.join(wd, "htest-out.txt")
    with open(msg, "w") as stdo:
        stdo.write(" ".join(argv) + "\n")
        stdo.flush()
        rc = subprocess.call(argv,
                             stdin=devnull,
                             stdout=stdo,
                             stderr=subprocess.STDOUT,
                             cwd=wd)
        if rc != 0:
            stdo.write("exit {0}\n".format(rc))
    return (rc, msg)

def probe_one(wd, cc, header, known_headers, devnull):
    src = gensrc(wd, header, known_headers)
    (rc, msg) = invoke(wd, devnull, [cc, "-c", src])
    if rc == 0:
        return True
    with open(msg, "rU") as f: errors = f.read()

    (rc, msg) = invoke(wd, devnull, [cc, "-E", src])
    if rc == 0:
        sys.stderr.write("# {0} present but cannot be compiled:\n"
                         .format(header))
        for e in errors.split("\n"): sys.stderr.write("# {0}\n".format(e))

    return False

def probe(compiler, headers):
    wd=None
    known_headers = set()
    try:
        wd = tempfile.mkdtemp()
        with open(os.devnull, "rb") as devnull:
            for h in headers:
                if h.startswith("SPECIAL_") and not h.endswith(".h"):
                    continue
                if probe_one(wd, compiler, h, known_headers, devnull):
                    known_headers.add(h)
    finally:
        if wd is not None:
            shutil.rmtree(wd)

    return known_headers

if __name__ == '__main__':
    compiler = "cc"
    if len(sys.argv) > 1:
        compiler = sys.argv[1]
    avail_headers = probe(compiler, sorted_common_headers())
    un = os.uname()
    sys.stdout.write("# " + un[0] + " " + un[2] + " " + un[4] + "\n")
    sys.stdout.write(":category unknown\n:label unknown\n")
    for h in sortheaders.hsorted(avail_headers):
        sys.stdout.write(h + "\n")
