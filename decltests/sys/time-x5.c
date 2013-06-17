/* baseline */
#include <sys/time.h>

void f(void)
{
  struct timeval tv;
  time_t      *tvs = &tv.tv_sec;
  suseconds_t *tvu = &tv.tv_usec;
  struct itimerval it, iu;
  struct timeval *iti = &it.it_interval;
  struct timeval *itv = &it.it_value;

  fd_set fds;
  /* XPG4.2 does specify the contents of this structure but it is
     better to treat it as opaque. */

  int
    ia = ITIMER_REAL,
    ib = ITIMER_VIRTUAL,
    ic = ITIMER_PROF;

  unsigned long id = FD_SETSIZE;

  FD_ZERO(&fds);
  FD_CLR(0, &fds);
  FD_SET(1, &fds);
  int a = FD_ISSET(2, &fds);

  int b = getitimer(ia, &it);
  int c = setitimer(ia, &it, &iu);
  int d = gettimeofday(&tv, 0);
  int e = select(4, &fds, 0, 0, &tv);

  struct timeval tf[2];
  int f = utimes("thingy", tf);
}
