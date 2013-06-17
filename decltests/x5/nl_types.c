#include <nl_types.h>

void f(int aa, int bb, const char *cc)
{
  int a = NL_SETD;
  int b = NL_CAT_LOCALE;
  nl_item c;

  nl_catd d = catopen(cc, aa);
  char   *e = catgets(d, aa, bb, cc);
  int     f = catclose(d);
}
