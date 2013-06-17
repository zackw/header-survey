#include <strings.h>

/* LEGACY skipped: bcmp, bcopy, bzero, index, rindex */

void f(int aa, const char *bb, const char *cc, size_t dd)
{
  int a = ffs(aa);
  int b = strcasecmp(bb, cc);
  int c = strncasecmp(bb, cc, dd);
}
