/* <code>va_copy</code> */
#include <stdarg.h>

void fn(int x, ...)
{
  va_list ap1, ap2;
  va_start(ap1, x);
  va_copy(ap2, ap1);
  va_end(ap2);
  va_end(ap1);
}
