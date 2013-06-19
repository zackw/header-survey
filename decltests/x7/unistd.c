/* features */
#include <unistd.h>

int ic[] = {
  _CS_POSIX_V7_ILP32_OFF32_CFLAGS,
  _CS_POSIX_V7_ILP32_OFF32_LDFLAGS,
  _CS_POSIX_V7_ILP32_OFF32_LIBS,
  _CS_POSIX_V7_ILP32_OFFBIG_CFLAGS,
  _CS_POSIX_V7_ILP32_OFFBIG_LDFLAGS,
  _CS_POSIX_V7_ILP32_OFFBIG_LIBS,
  _CS_POSIX_V7_LP64_OFF64_CFLAGS,
  _CS_POSIX_V7_LP64_OFF64_LDFLAGS,
  _CS_POSIX_V7_LP64_OFF64_LIBS,
  _CS_POSIX_V7_LPBIG_OFFBIG_CFLAGS,
  _CS_POSIX_V7_LPBIG_OFFBIG_LDFLAGS,
  _CS_POSIX_V7_LPBIG_OFFBIG_LIBS,
  _CS_POSIX_V7_THREADS_CFLAGS,
  _CS_POSIX_V7_THREADS_LDFLAGS,
  _CS_POSIX_V7_WIDTH_RESTRICTED_ENVS,
  _CS_V7_ENV,

  _PC_REC_MAX_XFER_SIZE,
  _PC_TIMESTAMP_RESOLUTION,

  _SC_THREAD_ROBUST_PRIO_INHERIT,
  _SC_THREAD_ROBUST_PRIO_PROTECT,
  _SC_V7_ILP32_OFF32,
  _SC_V7_ILP32_OFFBIG,
  _SC_V7_LP64_OFF64,
  _SC_V7_LPBIG_OFFBIG,
  _SC_XOPEN_UUCP,
};

void f(void)
{
  int          faccessat(int, const char *, int, int);
  int          fchownat(int, const char *, uid_t, gid_t, int);
  int          fexecve(int, char *const [], char *const []);
  int          linkat(int, const char *, int, const char *, int);
  ssize_t      readlinkat(int, const char *restrict, char *restrict, size_t);
  int          symlinkat(const char *, int, const char *);
  int          unlinkat(int, const char *, int);
}
