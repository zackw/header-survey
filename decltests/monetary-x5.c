/* baseline */
#include <monetary.h>

void f(void)
{
  char buf[20];
  size_t ss = sizeof buf;
  ssize_t r = strfmon(buf, ss, "%#9.2n", 299999.99);
}
