/* SUSv2 additions */
#include <stdio.h>

static const char ptmpdir[] = ""P_tmpdir"";

void f(void)
{
  char a[L_ctermid];
  char *b = ctermid(a);
  va_list c;

  FILE *d = fdopen(1, "r+");
  int   e = fileno(d);

  flockfile(d);
  int f = ftrylockfile(d);
  funlockfile(d);

  int i = getc_unlocked(d);
  int j = getchar_unlocked();
  int k = putc_unlocked('x', d);
  int l = putchar_unlocked('x');
  int m = getw(d);
  int n = putw(m, d);

  FILE *o = popen("ls", "r");
  int p = pclose(o);

  char *q = tempnam(NULL, "abba");
}

/* off_t not necessarily exposed in stdio.h, even though fseeko/ftello are */
#include <sys/types.h>

void g(FILE *aa)
{
  off_t a = ftello(aa);
  int b = fseeko(aa, a, SEEK_END);
}
