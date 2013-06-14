/* baseline */
#include <fnmatch.h>

void f(void)
{
  int
    a = FNM_NOMATCH,
    b = FNM_PATHNAME,
    c = FNM_PERIOD,
    d = FNM_NOESCAPE,
    e = FNM_NOSYS;

  int f = fnmatch("a*b", "accccb", 0);
}
