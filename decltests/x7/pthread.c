/* robust mutexes */
#include <pthread.h>

int xx[] = {
  PTHREAD_MUTEX_ROBUST,
  PTHREAD_MUTEX_STALLED,
};

void f(void)
{
  int (*a)(pthread_mutex_t *) = pthread_mutex_consistent;
  int (*b)(const pthread_mutexattr_t *, int *) = pthread_mutexattr_getrobust;
  int (*c)(pthread_mutexattr_t *, int) = pthread_mutexattr_setrobust;
}
