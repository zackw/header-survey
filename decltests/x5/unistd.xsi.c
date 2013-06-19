/* XSI: features */
#include <unistd.h>

#ifndef _XOPEN_VERSION
#error "_XOPEN_VERSION"
#endif

int ic[] = {
  F_LOCK, F_TEST, F_TLOCK, F_ULOCK,

  _CS_XBS5_ILP32_OFF32_CFLAGS,
  _CS_XBS5_ILP32_OFF32_LDFLAGS,
  _CS_XBS5_ILP32_OFF32_LIBS,
  _CS_XBS5_ILP32_OFF32_LINTFLAGS,
  _CS_XBS5_ILP32_OFFBIG_CFLAGS,
  _CS_XBS5_ILP32_OFFBIG_LDFLAGS,
  _CS_XBS5_ILP32_OFFBIG_LIBS,
  _CS_XBS5_ILP32_OFFBIG_LINTFLAGS,
  _CS_XBS5_LP64_OFF64_CFLAGS,
  _CS_XBS5_LP64_OFF64_LDFLAGS,
  _CS_XBS5_LP64_OFF64_LIBS,
  _CS_XBS5_LP64_OFF64_LINTFLAGS,
  _CS_XBS5_LPBIG_OFFBIG_CFLAGS,
  _CS_XBS5_LPBIG_OFFBIG_LDFLAGS,
  _CS_XBS5_LPBIG_OFFBIG_LIBS,
  _CS_XBS5_LPBIG_OFFBIG_LINTFLAGS,
};

useconds_t tg;

void f(void)
{
  char        *(*ai)(const char *, const char *) = crypt;
  void         (*an)(char[64], int) = encrypt;
  int          (*aw)(int) = fchdir;
  long         (*bi)(void) = gethostid;
  pid_t        (*bo)(pid_t) = getpgid;
  pid_t        (*bs)(pid_t) = getsid;
  int          (*bw)(const char *, uid_t, gid_t) = lchown;
  int          (*by)(int, int, off_t) = lockf;
  int          (*ca)(int) = nice;
  ssize_t      (*ce)(int, void *, size_t, off_t) = pread;
  ssize_t      (*cg)(int, const void *, size_t, off_t) = pwrite;
  pid_t        (*cn)(void) = setpgrp;
  int          (*co)(gid_t, gid_t) = setregid;
  int          (*cp)(uid_t, uid_t) = setreuid;
  void         (*ct)(const void *, void *, ssize_t) = swab;
  void         (*cv)(void) = sync;
  int          (*cz)(const char *, off_t) = truncate;
  useconds_t   (*dc)(useconds_t, useconds_t) = ualarm;
  int          (*de)(useconds_t) = usleep;
  pid_t        (*df)(void) = vfork;
}
