/* <code>mprotect</code> */
#include <sys/mman.h>

int cc[] = {
  PROT_READ,
  PROT_WRITE,
  PROT_EXEC,
  PROT_NONE,
};

void f(void *aa, size_t bb)
{
  int a = mprotect(aa, bb, PROT_READ|PROT_WRITE|PROT_EXEC);
}
