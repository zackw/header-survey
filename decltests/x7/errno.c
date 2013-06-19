/* <code>ENOTRECOVERABLE</code> and <code>EOWNERDEAD</code> (POSIX.1-2008) */
#include <errno.h>

void fn(void)
{
  errno = ENOTRECOVERABLE;
  errno = EOWNERDEAD;
}
