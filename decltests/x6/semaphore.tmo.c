/* <code>sem_timedwait</code> */
#include <semaphore.h>

void f(void)
{
  int (*a)(sem_t *, const struct timespec *) = sem_timedwait;
}
