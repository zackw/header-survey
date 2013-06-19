/* <code>mlock</code>, <code>munlock</code>, <code>mlockall</code>, <code>munlockall</code> */
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
}
