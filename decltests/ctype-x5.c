/* SUSv2 additions (all obsolete in POSIX-2008) */
#include <ctype.h>

void f(int aa)
{
  /* must be functions, may also be macros */
  int a = isascii(aa);
  int b = toascii(aa);
  int c = (isascii)(aa);
  int d = (toascii)(aa);

  /* only required to be macros */
  int e = _toupper(aa);
  int f = _tolower(aa);
}
