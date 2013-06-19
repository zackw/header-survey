/* process-shared thread barriers */
#include <pthread.h>

void f(void)
{
  int (*a)(const pthread_barrierattr_t *, int *)
    = pthread_barrierattr_getpshared;
  int (*b)(pthread_barrierattr_t *, int)
    = pthread_barrierattr_setpshared;
}
