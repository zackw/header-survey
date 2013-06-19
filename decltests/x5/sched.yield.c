/* optional: <code>sched_yield</code> */
#include <sched.h>

void f(void)
{
  int (*h)(void) = sched_yield;
}
