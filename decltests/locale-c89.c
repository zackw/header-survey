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

  char **a = &lc->decimal_point;
  char **b = &lc->thousands_sep;
  char **c = &lc->grouping;
  char **d = &lc->mon_decimal_point;
  char **e = &lc->mon_thousands_sep;
  char **f = &lc->mon_grouping;
  char **g = &lc->positive_sign;
  char **h = &lc->negative_sign;
  char **i = &lc->currency_symbol;
  char  *j = &lc->frac_digits;
  char  *k = &lc->p_cs_precedes;
  char  *l = &lc->n_cs_precedes;
  char  *m = &lc->p_sep_by_space;
  char  *n = &lc->n_sep_by_space;
  char  *o = &lc->p_sign_posn;
  char  *p = &lc->n_sign_posn;
  char **q = &lc->int_curr_symbol;
  char  *r = &lc->int_frac_digits;
}
