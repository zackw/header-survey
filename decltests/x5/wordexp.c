#include <wordexp.h>

/* WRDE_NOSYS obsolete in issue 6, removed in 7 */

int flags[] = {
  WRDE_APPEND,
  WRDE_DOOFFS,
  WRDE_NOCMD,
  WRDE_REUSE,
  WRDE_SHOWERR,
  WRDE_UNDEF,
};

int errs[] = {
  WRDE_BADCHAR,
  WRDE_BADVAL,
  WRDE_CMDSUB,
  WRDE_NOSPACE,
  WRDE_SYNTAX,
};

void f(wordexp_t *aa, const char *bb, int cc)
{
  size_t *a = &aa->we_wordc;
  char ***b = &aa->we_wordv;
  size_t *c = &aa->we_offs;

  int d = wordexp(bb, aa, cc);
  wordfree(aa);
}
