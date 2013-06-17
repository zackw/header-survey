/* additional C99 error codes */
#include <errno.h>

void fn(void)
{
  errno = EILSEQ;
}
