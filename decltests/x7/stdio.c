/* features */
#include <stdio.h>

void f(void)
{
  int     (*a)(int, const char *, ...) = dprintf;
  FILE   *(*b)(void *, size_t, const char *) = fmemopen;
  ssize_t (*c)(char **, size_t *, int, FILE *) = getdelim;
  ssize_t (*d)(char **, size_t *, FILE *) = getline;
  FILE   *(*e)(char **, size_t *) = open_memstream;
  int     (*f)(int, const char *, int, const char *) = renameat;
  int     (*g)(int, const char *, va_list) = vdprintf;
}
