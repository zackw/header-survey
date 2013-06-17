/* baseline */
#include <sys/mman.h>

int cc[] = {
  PROT_READ,
  PROT_WRITE,
  PROT_EXEC,
  PROT_NONE,

  MAP_SHARED,
  MAP_PRIVATE,
  MAP_FIXED,

  MS_ASYNC,
  MS_SYNC,
  MS_INVALIDATE
};

void f(int aa, size_t bb, off_t cc)
{
  void *a = mmap(0, bb, PROT_READ|PROT_WRITE, MAP_SHARED, aa, cc);
  int   b = mprotect(a, bb, PROT_READ|PROT_WRITE|PROT_EXEC);
  int   c = msync(a, bb, MS_ASYNC);
  int   d = munmap(a, bb);
}
