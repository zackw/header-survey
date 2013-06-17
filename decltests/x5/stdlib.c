/* additional POSIX and XSI functions */
#include <stdlib.h>

/* "defined as in sys/wait.h, for decoding the return value from system()" */
void wmacros(int ss)
{
  int
    a = WNOHANG,
    b = WUNTRACED,
    c = WEXITSTATUS(ss),
    d = WIFEXITED(ss),
    e = WIFSIGNALED(ss),
    f = WIFSTOPPED(ss),
    g = WSTOPSIG(ss),
    h = WTERMSIG(ss);
}

void f(const char *aa, long bb, unsigned short cc[3],
       unsigned short dd[7], double ee, int ff,
       char *gg, char *const *hh, int ii, unsigned int *jj, size_t kk)
{
  long  a = a64l(aa);
  char *b = l64a(bb);

  int   c = rand_r(jj);
  char *d = initstate(*jj, gg, kk);
  long  e = random();
  char *f = setstate(d);
  srandom(*jj);

  double g = drand48();
  double h = erand48(cc);
  long   i = jrand48(cc);
  lcong48(dd);
  long   j = lrand48();
  long   k = mrand48();
  long   l = nrand48(cc);
  unsigned short *m = seed48(cc);
  srand48(bb);

  char buf[4096];
  int decpt, sign;
  char *n = ecvt(ee, ff, &decpt, &sign);
  char *o = fcvt(ee, ff, &decpt, &sign);
  char *p = gcvt(ee, ff, buf);

  int   q = grantpt(ii);
  int   r = unlockpt(ii);
  char *s = ptsname(ii);
  char *t = realpath(aa, buf);
  int   u = putenv(gg);
  char *v = mktemp(gg);
  int   w = mkstemp(gg);

  /* paired with functions in unistd.h - getopt, encrypt respectively */
  char *x;
  int y = getsubopt(&gg, hh, &x);
  setkey(aa);
}

/* LEGACY declarations skipped: ttyslot(), valloc() */
