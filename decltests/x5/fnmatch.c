#include <fnmatch.h>

void f(void)
{
  int
    a = FNM_NOMATCH,
    b = FNM_PATHNAME,
    c = FNM_PERIOD,
    d = FNM_NOESCAPE;
  /* FNM_NOSYS obsolete in Issue 6, removed in Issue 7 */

  int f = fnmatch("a*b", "accccb", 0);
}
