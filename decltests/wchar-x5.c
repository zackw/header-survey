/* SUSv2 additions */
#define _XOPEN_SOURCE 500
#include <wchar.h>

void f(const wchar_t *ss, size_t nn, wchar_t dd)
{
  int a = wcswidth(ss, nn);
  int b = wcwidth(dd);
}
