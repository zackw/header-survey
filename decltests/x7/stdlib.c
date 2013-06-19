/* <code>mkdtemp</code> */
#include <stdlib.h>

void f(void)
{
  char *(*a)(char *) = mkdtemp;
}
