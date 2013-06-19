/* <code>shm_open</code> and <code>shm_unlink</code> */
#include <sys/mman.h>

void f(const char *bb, int cc, mode_t dd)
{
  int e = shm_open(bb, cc, dd);
  int f = shm_unlink(bb);
}
