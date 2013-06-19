/* <code>memccpy</code> and <code>strdup</code> (XSI) */
#include <string.h>

void f(char *a, char *b, size_t c)
{
  char *d = memccpy(a, b, 'x', c);
  char *e = strdup(b);
}
