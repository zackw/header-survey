/* additional POSIX.1-2008 functions and constants */
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
