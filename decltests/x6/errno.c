/* <code>ENETRESET</code> (POSIX.1-2001) */
#include <errno.h>

void fn(void)
{
  errno = ENETRESET;
}
