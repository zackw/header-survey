/* <code>fsync</code> */
#include <unistd.h>

void f(void)
{
  int          (*ba)(int) = fsync;
}
