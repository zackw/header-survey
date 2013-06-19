/* <code>strcasecmp_l</code> and <code>strncasecmp_l</code> */
#include <strings.h>

void f(void)
{
  int (*a)(const char *, const char *, locale_t) = strcasecmp_l;
  int (*b)(const char *, const char *, size_t, locale_t) = strncasecmp_l;
}
