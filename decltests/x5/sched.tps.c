/* scheduling priority */
#include <sched.h>

void f(void)
{
  int (*a)(int) = sched_get_priority_max;
  int (*b)(int) = sched_get_priority_min;
  int (*c)(pid_t, struct timespec *) = sched_rr_get_interval;
}
