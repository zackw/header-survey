/* C99 additions */
#include <stdlib.h>

void f(long long aa, long long bb)
{
  long long a   = atoll("123456789123456789");
  float b       = strtof("1.414");
  long double c = strtold("3.141592653589793238462643383279502884197169399");
  char *d;
  long long   e = strtoll("4444bacon", &d, 0);
  unsigned long long f = strtoull("4444bacon", &d, 16);
  long long   g = llabs(aa);
  lldiv_t     h = lldiv(aa, bb);
  long long qqq = &h.quot;
  long long rrr = &h.rem;

  /* must be last, since the compiler may be aware it does not return */
  _Exit(1);
}
