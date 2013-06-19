/* signal functions for specific threads */
#include <signal.h>

void f(void)
{
  int (*a)(pthread_t, int) = pthread_kill;
  int (*b)(int, const sigset_t *, sigset_t *) = pthread_sigmask;
}
