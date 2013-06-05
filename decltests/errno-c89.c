/* baseline */
#include <errno.h>

void fn(void)
{
  int x = errno;
  errno = EDOM;
  errno = ERANGE;
}
