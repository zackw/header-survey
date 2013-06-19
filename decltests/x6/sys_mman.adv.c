/* <code>posix_madvise</code> */
#include <sys/mman.h>

int cc[] = {
  POSIX_MADV_NORMAL,
  POSIX_MADV_SEQUENTIAL,
  POSIX_MADV_RANDOM,
  POSIX_MADV_WILLNEED,
  POSIX_MADV_DONTNEED,
};

void f(void)
{
  int (*a)(void *, size_t, int) = posix_madvise;
}
