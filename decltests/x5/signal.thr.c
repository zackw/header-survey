/* optional: <code>pthread_kill</code> and <code>pthread_sigmask</code> */
#include <signal.h>

void f(void)
{
  int (*a)(pthread_t, int) = pthread_kill;
  int (*b)(int, const sigset_t *, sigset_t *) = pthread_sigmask;
}
