/* <code>msync</code> */
#include <sys/mman.h>

int cc[] = {
  MS_ASYNC,
  MS_SYNC,
  MS_INVALIDATE,
};

void f(void *a, size_t bb)
{
  int c = msync(a, bb, MS_ASYNC);
}
