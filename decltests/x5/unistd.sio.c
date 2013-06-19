/* <code>fdatasync</code> */
#include <unistd.h>

void f(void)
{
  int          (*ax)(int) = fdatasync;
}
