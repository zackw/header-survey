/* <code>mmap</code> and <code>munmap</code> */
#include <sys/mman.h>

int cc[] = {
  PROT_READ,
  PROT_WRITE,
  PROT_EXEC,
  PROT_NONE,

  MAP_SHARED,
  MAP_PRIVATE,
  MAP_FIXED,
};

void f(int aa, size_t bb, off_t cc)
{
  void *a = mmap(0, bb, PROT_READ|PROT_WRITE, MAP_SHARED, aa, cc);
  void *b = MAP_FAILED;
  int   d = munmap(a, bb);
}
