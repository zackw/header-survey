/* <code>strftime_l</code> */
#include <time.h>

void f(void)
{
  size_t (*a)(char *, size_t, const char *, const struct tm *, locale_t)
    = strftime_l;
}
