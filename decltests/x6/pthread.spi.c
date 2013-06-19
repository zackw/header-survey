/* optional: spinlock functions */
#include <pthread.h>

void f(void)
{
  pthread_spinlock_t x;
  int   (*a)(pthread_spinlock_t *) = pthread_spin_destroy;
  int   (*b)(pthread_spinlock_t *, int) = pthread_spin_init;
  int   (*c)(pthread_spinlock_t *) = pthread_spin_lock;
  int   (*d)(pthread_spinlock_t *) = pthread_spin_trylock;
  int   (*e)(pthread_spinlock_t *) = pthread_spin_unlock;
}
