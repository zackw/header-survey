/* <code>ENOTRECOVERABLE</code> and <code>EOWNERDEAD</code> */
#include <errno.h>

void fn(void)
{
  errno = ENOTRECOVERABLE;
  errno = EOWNERDEAD;
}
