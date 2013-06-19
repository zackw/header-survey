/* optional: <code>clock_getcpuclockid</code> */
#include <time.h>

void f(void)
{
  int (*a)(pid_t, clockid_t *) = clock_getcpuclockid;
}
