/* "advisory" functions (POSIX.1-2001 optional) */
#include <fcntl.h>

int cc[] = {
  POSIX_FADV_NORMAL,
  POSIX_FADV_SEQUENTIAL,
  POSIX_FADV_RANDOM,
  POSIX_FADV_WILLNEED,
  POSIX_FADV_DONTNEED,
  POSIX_FADV_NOREUSE,
};

void f(void)
{
  int (*a)(int, off_t, off_t, int) = posix_fadvise;
  int (*b)(int, off_t, off_t) = posix_fallocate;
}
