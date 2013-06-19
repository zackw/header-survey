#include <sched.h>

int xx[] = {
  SCHED_FIFO,
  SCHED_RR,
  SCHED_OTHER
};

void f(void)
{
  struct sched_param bb;
  int *bbp = &bb.sched_priority;

  int (*a)(pid_t, struct sched_param *) = sched_getparam;
  int (*b)(pid_t) = sched_getscheduler;
  int (*c)(pid_t, const struct sched_param *) = sched_setparam;
  int (*d)(pid_t, int, const struct sched_param *) = sched_setscheduler;
}
