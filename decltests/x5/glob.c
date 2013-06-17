#include <glob.h>

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

  int
    ga = GLOB_APPEND,
    gb = GLOB_DOOFFS,
    gc = GLOB_ERR,
    gd = GLOB_MARK,
    ge = GLOB_NOCHECK,
    gf = GLOB_NOESCAPE,
    gg = GLOB_NOSORT,
    gh = GLOB_ABORTED,
    gi = GLOB_NOMATCH,
    gj = GLOB_NOSPACE,
    gk = GLOB_NOSYS;

  int a = glob(aa, bb, ee, &cc);
  globfree(&cc);
}
