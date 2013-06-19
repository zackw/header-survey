/* functions */
#include <wchar.h>

/* note: C89/C99 distinction for this header deduced by comparing
   SUSv2 to C99, as I don't have an official copy of C89.  May not be
   100% accurate. */

void f(const wchar_t *ss)
{
  wchar_t *ee;

  float              a = wcstof(ss, &ee);
  long double        b = wcstold(ss, &ee);
  long long          c = wcstoll(ss, &ee, 10);
  unsigned long long d = wcstoull(ss, &ee, 10);
}

#include <stdarg.h>
/* in strict ISO C compliance mode FILE is not visible from wchar.h */
#include <stdio.h>

void vf(FILE *ff, const wchar_t *bb, const wchar_t *ss, ...)
{
  va_list ap;
  va_start(ap, ss);

  int a = vfwscanf(ff, ss, ap);
  int b = vwscanf(ss, ap);
  int c = vswscanf(bb, ss, ap);
}
