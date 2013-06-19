/* additional threading support */
#include <stdio.h>

void f(FILE *d)
{
  flockfile(d);
  int f = ftrylockfile(d);
  funlockfile(d);

  int i = getc_unlocked(d);
  int j = getchar_unlocked();
  int k = putc_unlocked('x', d);
  int l = putchar_unlocked('x');
}
