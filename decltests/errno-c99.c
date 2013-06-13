/* C99: error constants */
#include <errno.h>

void fn(void)
{
  errno = EILSEQ;
}
