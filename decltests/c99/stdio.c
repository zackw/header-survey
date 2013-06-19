/* functions */
#include <stdio.h>

void fn(void)
{
  char b[BUFSIZ];
  int a = snprintf(b, BUFSIZ, "%s\n", "text");
}

#include <stdarg.h>

/* N.B. I'm not sure whether v*scanf really weren't in C89. */

void vfn(const char *m, ...)
{
  va_list ap;
  int a, c, d, e;
  char b[BUFSIZ];
  va_start(ap, m);
  a = vsnprintf(b, BUFSIZ, m, ap);
  c = vfscanf(stdin, m, ap);
  d = vscanf(m, ap);
  e = vsscanf(b, m, ap);
  va_end(ap);
}
