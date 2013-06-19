/* support for sporadic server scheduling policy */
#include <sched.h>

#if defined _POSIX_SPORADIC_SERVER || defined _POSIX_THREAD_SPORADIC_SERVER

int xx[] = {
  SCHED_SPORADIC,
};

void f(void)
{
  struct sched_param bb;
  int             *bbl = &bb.sched_ss_low_priority;
  struct timespec *bbp = &bb.sched_ss_repl_period;
  struct timespec *bbi = &bb.sched_ss_init_budget;
  int             *bbm = &bb.sched_ss_max_repl;
}

#else
#error "no sporadic server scheduling policy"
#endif
