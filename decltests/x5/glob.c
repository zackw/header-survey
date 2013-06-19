#include <glob.h>

int xx[] = {
  GLOB_APPEND,
  GLOB_DOOFFS,
  GLOB_ERR,
  GLOB_MARK,
  GLOB_NOCHECK,
  GLOB_NOESCAPE,
  GLOB_NOSORT,
  GLOB_ABORTED,
  GLOB_NOMATCH,
  GLOB_NOSPACE,
  /* GLOB_NOSYS,  obsolescent in Issue 6, removed in 7 */
};

int ee(const char *a, int b)
{
  return 0;
}

void f(const char *aa, int bb)
{
  glob_t cc;
  size_t *cca = &cc.gl_pathc;
  char ***ccb = &cc.gl_pathv;
  size_t *ccc = &cc.gl_offs;

  int a = glob(aa, bb, ee, &cc);
  globfree(&cc);
}
