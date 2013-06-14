/* baseline */
#include <fmtmsg.h>

int f(void)
{
  int
    a = MM_HARD,
    b = MM_SOFT,
    c = MM_FIRM,
    d = MM_APPL,
    e = MM_UTIL,
    f = MM_OPSYS,
    g = MM_RECOVER,
    h = MM_NRECOV,
    i = MM_HALT,
    j = MM_ERROR,
    k = MM_WARNING,
    l = MM_INFO,
    n = MM_NOSEV,
    o = MM_PRINT,
    p = MM_CONSOLE,
    q = MM_OK,
    r = MM_NOTOK,
    s = MM_NOMSG,
    t = MM_NOCON,
    u = MM_NULLSEV;
  long v = MM_NULLMC;
  char
    *w = MM_NULLLBL,
    *x = MM_NULLTXT,
    *y = MM_NULLACT,
    *z = MM_NULLTAG;

  return fmtmsg(v, w, u, x, y, z);
}
