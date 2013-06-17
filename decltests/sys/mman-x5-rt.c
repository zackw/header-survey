/* SUSv2: realtime extensions */
#include <sys/mman.h>

int cc[] = {
  MCL_CURRENT,
  MCL_FUTURE
};

void f(const void *aa, const char *bb, int cc, mode_t dd)
{
  int a = mlock(aa, 1024*1024);
  int b = mlockall(MCL_CURRENT);
  int c = munlock(aa, 1024*1024);
  int d = munlockall();
  int e = shm_open(bb, cc, dd);
  int f = shm_unlink(bb);
}
