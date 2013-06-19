/* features */
#include <string.h>

void f(locale_t ll, char *aa, char *bb)
{
  char *a  = strerror_l(1, ll);
  char *b  = stpcpy(aa, bb);
  char *c  = stpncpy(aa, bb, 99);
  char *d  = strndup(aa, 99);
  size_t e = strnlen(aa, 99);
  char *f  = strsignal(1);
  int g    = strcoll_l(aa, bb, ll);
  size_t h = strxfrm_l(aa, bb, 99, ll);
}
