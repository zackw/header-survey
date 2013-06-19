/* <code>getitimer</code> and <code>setitimer</code> */
#include <sys/time.h>

/* These are marked obsolete in Issue 7, but with no mention of it in
   the change log. Possibly considered superseded by timer_create et al? */

void f(void)
{
  struct itimerval it, iu;
  struct timeval *iti = &it.it_interval;
  struct timeval *itv = &it.it_value;

  int
    ia = ITIMER_REAL,
    ib = ITIMER_VIRTUAL,
    ic = ITIMER_PROF;

  int b = getitimer(ia, &it);
  int c = setitimer(ia, &it, &iu);
}
