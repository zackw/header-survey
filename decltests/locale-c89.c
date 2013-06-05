/* baseline */
#include <locale.h>

void m(void)
{
  char *p = NULL;
  int a = LC_ALL;
  int b = LC_COLLATE;
  int c = LC_CTYPE;
  int d = LC_MONETARY;
  int e = LC_NUMERIC;
  int f = LC_TIME;
}

void f(void)
{
  char *sl = setlocale(LC_ALL, "");
  struct lconv *lc = localeconv();

  char *a = lc->decimal_point;
  char *b = lc->thousands_sep;
  char *c = lc->grouping;
  char *d = lc->int_curr_symbol;
  char *e = lc->currency_symbol;
  char *f = lc->mon_decimal_point;
  char *g = lc->mon_thousands_sep;
  char *h = lc->mon_grouping;
  char *i = lc->positive_sign;
  char *j = lc->negative_sign;
  char  k = lc->int_frac_digits;
  char  l = lc->frac_digits;
  char  m = lc->p_cs_precedes;
  char  n = lc->p_sep_by_space;
  char  o = lc->n_cs_precedes;
  char  p = lc->n_sep_by_space;
  char  q = lc->p_sign_posn;
  char  r = lc->n_sign_posn;
}
