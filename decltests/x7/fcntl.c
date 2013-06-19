/* features */
#include <fcntl.h>

int cc[] = {
  F_DUPFD_CLOEXEC,
  FD_CLOEXEC,
  O_CLOEXEC,
  O_DIRECTORY,
  O_NOFOLLOW,
  O_TTY_INIT,
};

int (*f)(int, const char *, int, ...) = openat;
