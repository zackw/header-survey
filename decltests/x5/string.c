/* additional POSIX and XSI functions */
#include <string.h>

void f(char *a, char *b, size_t c)
{
  char *d = memccpy(a, b, 'x', c);
  char *e = strdup(b);
  char *f;
  char *g = strtok_r(a, ":;", &f);
}
