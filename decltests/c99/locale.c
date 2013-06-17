/* additional <code>struct lconv</code> members (C99) */
#include <locale.h>

void f(struct lconv *lc)
{
  char *a = &lc->int_p_cs_precedes;
  char *b = &lc->int_n_cs_precedes;
  char *c = &lc->int_p_sep_by_space;
  char *d = &lc->int_n_sep_by_space;
  char *e = &lc->int_p_sign_posn;
  char *f = &lc->int_n_sign_posn;
}
