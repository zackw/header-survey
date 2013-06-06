/* POSIX.1-1996: additional functions */
#define _POSIX_C_SOURCE 199506L
#include <string.h>

void f(char *a, char *b, size_t c)
{
  char *d = memccpy(a, b, 'x', c);
  char *e = strdup(b);
  char *f;
  char *g = strtok_r(a, ":;", &f);
}
