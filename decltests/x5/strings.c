#include <strings.h>

/* LEGACY skipped: bcmp, bcopy, bzero, index, rindex */

/* technically the entire header was XSI in Issue 5/6, but Issue 7
   promoted str*casecmp to Base */

void f(int aa, const char *bb, const char *cc, size_t dd)
{
  int b = strcasecmp(bb, cc);
  int c = strncasecmp(bb, cc, dd);
}
