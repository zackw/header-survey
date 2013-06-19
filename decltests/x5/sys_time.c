/* <code>gettimeofday</code> and <code>struct timeval</code> */
#include <sys/time.h>

/* This is the function most commonly wanted from <sys/time.h>.
   Issue 7 obsolesces it without mention in the change log --
   I suppose arguably it's superseded by clock_gettime.  Anyhow
   I'm not dropping it at least till I see whether Issue 8 will
   actually remove it. */

void f(void)
{
  struct timeval tv;
  time_t      *tvs = &tv.tv_sec;
  suseconds_t *tvu = &tv.tv_usec;

  int d = gettimeofday(&tv, 0);
}
