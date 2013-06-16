/* POSIX.1-2001: additional functions */
#include <string.h>

char buf[256];

int f (int n)
{
  return strerror_r(n, buf, sizeof buf);
}
