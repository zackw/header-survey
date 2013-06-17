/* additional C99 functions */
#include <stdlib.h>

void f(long long aa, long long bb)
{
  long long a   = atoll("123456789123456789");
  char *b;
  float c       = strtof("1.414", &b);
  long double d = strtold("3.14159265358979323846264338327950288419716939", &b);
  long long   e = strtoll("4444bacon", &b, 0);
  unsigned long long f = strtoull("4444bacon", &b, 16);
  long long   g = llabs(aa);
  lldiv_t     h = lldiv(aa, bb);
  long long *qq = &h.quot;
  long long *rr = &h.rem;

  /* must be last, since the compiler may be aware it does not return */
  _Exit(1);
}
