/* optional: lock functions with timeouts */
#include <pthread.h>

void f(void)
{
  int (*a)(pthread_mutex_t *, const struct timespec *)
    = pthread_mutex_timedlock;
  int (*b)(pthread_rwlock_t *, const struct timespec *)
    = pthread_rwlock_timedrdlock;
  int (*c)(pthread_rwlock_t *, const struct timespec *)
    = pthread_rwlock_timedwrlock;
}
