#include <stdarg.h>

void fn(int x, ...)
{
  va_list ap;
  int a; double b;
  va_start(ap, x);
  a = va_arg(ap, int);
  b = va_arg(ap, double);
  va_end(ap);
}
