/* <code>strfmon_l</code> */
#include <monetary.h>

void f(locale_t ll)
{
  char buf[20];
  size_t ss = sizeof buf;
  ssize_t r = strfmon_l(buf, ss, ll, "%#9.2n", 299999.99);
}
