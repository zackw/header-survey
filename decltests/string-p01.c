/* POSIX.1-2001: additional functions */
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED
#define _REENTRANT
#define _THREAD_SAFE
#include <string.h>

char buf[256];

int f (int n)
{
  return strerror_r(n, buf, sizeof buf);
}
