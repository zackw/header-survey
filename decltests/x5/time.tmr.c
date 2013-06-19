/* optional: timer support */
#include <time.h>

void f(void)
{
  clockid_t xx = CLOCK_REALTIME;
  int       xy = TIMER_ABSTIME;

  struct timespec cc;
  time_t *ccs = &cc.tv_sec;
  /* tv_nsec is spec'd as bare 'long' but may not actually be that
     type (depending on the ABI), so we just make sure it exists and
     can hold the largest value it's required to hold.  */
  cc.tv_nsec = 999999999L;

  struct itimerspec dd;
  struct timespec *ddi = &dd.it_interval;
  struct timespec *ddv = &dd.it_value;

  int (*a)(clockid_t, struct timespec *) = clock_getres;
  int (*b)(clockid_t, struct timespec *) = clock_gettime;
  int (*c)(clockid_t, const struct timespec *) = clock_settime;

  int (*d)(clockid_t, struct sigevent *, timer_t *) = timer_create;
  int (*e)(timer_t) = timer_delete;
  int (*f)(timer_t, struct itimerspec *) = timer_gettime;
  int (*g)(timer_t) = timer_getoverrun;
  int (*h)(timer_t, int, const struct itimerspec *, struct itimerspec *)
    = timer_settime;

  int (*i)(const struct timespec *, struct timespec *) = nanosleep;
}
