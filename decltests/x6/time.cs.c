/* <code>clock_nanosleep</code> */
#include <time.h>

void f(void)
{
  int (*a)(clockid_t, int, const struct timespec *,
           struct timespec *) = clock_nanosleep;
}
