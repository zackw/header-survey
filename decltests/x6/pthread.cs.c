/* thread clock controls */
#include <pthread.h>

void f(void)
{
  int (*a)(const pthread_condattr_t *, clockid_t *) = pthread_condattr_getclock;
  int (*b)(pthread_condattr_t *, clockid_t) = pthread_condattr_setclock;
  int (*c)(pthread_t, clockid_t *) = pthread_getcpuclockid;
}
