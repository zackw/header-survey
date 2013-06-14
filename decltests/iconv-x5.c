/* baseline */
#include <iconv.h>

void f(char **aa, size_t *bb, char **cc, size_t *dd)
{
  iconv_t *a = iconv_open("ascii", "utf-8");
  size_t   b = iconv(a, aa, bb, cc, dd);
  int      c = iconv_close(a);
}
