/* SUSv2: additional functions */
#define _XOPEN_SOURCE 500
#include <string.h>

void f(char *a, char *b, size_t c)
{
  char *d = memccpy(a, b, 'x', c);
  char *e = strdup(b);
  char *f;
  char *g = strtok_r(a, ":;", &f);
}
