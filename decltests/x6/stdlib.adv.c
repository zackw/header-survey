/* <code>posix_memalign</code> */
#include <stdlib.h>

void f(void)
{
  int (*a)(void **, size_t, size_t) = posix_memalign;
}
