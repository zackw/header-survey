/* optional: <code>sched_get_priority_min</code> and <code>sched_get_priority_max</code> */
#include <sched.h>

void f(void)
{
  int (*a)(int) = sched_get_priority_max;
  int (*b)(int) = sched_get_priority_min;
}
