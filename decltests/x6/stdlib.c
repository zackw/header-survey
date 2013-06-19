/* <code>setenv</code> and <code>unsetenv</code> */
#include <stdlib.h>

void f(void)
{
  int (*a)(const char *, const char *, int) = setenv;
  int (*b)(const char *) = unsetenv;
}
