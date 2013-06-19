/* <code>posix_openpt</code> */
#include <stdlib.h>

void f(void)
{
  int (*a)(int) = posix_openpt;
}
