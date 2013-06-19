/* XSI: features */
#include <wchar.h>

/* note: we do not check for the XSI requirement that all of
   <wctype.h> also appear in <wchar.h>, as this is marked "for
   backward compatibility only" in Issue 6, and officially
   obsoleted in Issue 7. */

void f(const wchar_t *ss, size_t nn, wchar_t dd)
{
  int a = wcswidth(ss, nn);
  int b = wcwidth(dd);
}
