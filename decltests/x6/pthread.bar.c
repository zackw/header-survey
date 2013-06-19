/* optional: thread barrier functions */
#include <pthread.h>

int xx[] = {
  PTHREAD_BARRIER_SERIAL_THREAD,
};

void f(void)
{
  pthread_barrier_t xa;
  pthread_barrierattr_t xb;

  int   (*a)(pthread_barrier_t *) = pthread_barrier_destroy;
  int   (*b)(pthread_barrier_t *, const pthread_barrierattr_t *, unsigned)
    = pthread_barrier_init;
  int   (*c)(pthread_barrier_t *) = pthread_barrier_wait;
  int   (*d)(pthread_barrierattr_t *) = pthread_barrierattr_destroy;
  int   (*e)(pthread_barrierattr_t *) = pthread_barrierattr_init;
}
