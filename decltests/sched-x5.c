/* baseline */
#include <sched.h>

void f(pid_t aa)
{
  struct sched_param bb;
  int *bbp = &bb.sched_priority;

  struct timespec cc;

  int a = sched_get_priority_max(SCHED_FIFO);
  int b = sched_get_priority_min(SCHED_RR);
  int c = sched_getparam(aa, &bb);
  int d = sched_getscheduler(aa);
  int e = sched_rr_get_interval(aa, &cc);
  int f = sched_setparam(aa, &bb);
  int g = sched_setscheduler(aa, SCHED_OTHER, &bb);
  int h = sched_yield();
}
