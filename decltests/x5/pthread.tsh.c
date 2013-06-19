/* optional: functions for process-shared synchronization */
#include <pthread.h>

void f(void)
{
  int (*a)(const pthread_condattr_t *, int *) = pthread_condattr_getpshared;
  int (*b)(pthread_condattr_t *, int) = pthread_condattr_setpshared;
  int (*c)(const pthread_mutexattr_t *, int *) = pthread_mutexattr_getpshared;
  int (*d)(pthread_mutexattr_t *, int) = pthread_mutexattr_setpshared;
  int (*e)(const pthread_rwlockattr_t *, int *) = pthread_rwlockattr_getpshared;
  int (*f)(pthread_rwlockattr_t *, int) = pthread_rwlockattr_setpshared;
}
