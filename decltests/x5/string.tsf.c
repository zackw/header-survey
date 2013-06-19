/* optional: <code>strtok_r</code> */
#include <string.h>

void f(char *a)
{
  char *f;
  char *g = strtok_r(a, ":;", &f);
}
