/* <code>strerror_r</code> */
#include <string.h>

char buf[256];

int f(int n)
{
  return strerror_r(n, buf, sizeof buf);
}
