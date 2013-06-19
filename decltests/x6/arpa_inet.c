/* additional POSIX.1-2001 functions and macros */
#include <arpa/inet.h>

void f(const void *aa, void *bb,
       const char *cc, char *dd,
       int ee, socklen_t ff)
{
  const char *a = inet_ntop(ee, aa, dd, ff);
  int b = inet_pton(ee, cc, bb);
  char c[INET_ADDRSTRLEN];
}
