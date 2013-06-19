#include <sys/select.h>

void f(void)
{
  struct timeval tv;
  time_t      *tvs = &tv.tv_sec;
  suseconds_t *tvu = &tv.tv_usec;
  struct timespec ts;
  time_t      *tss = &ts.tv_sec;
  /* tv_nsec is spec'd as bare 'long' but may not actually be that
     type (depending on the ABI), so we just make sure it exists and
     can hold the largest value it's required to hold.  */
  ts.tv_nsec = 999999999L;

  time_t xa;
  suseconds_t xb;
  sigset_t xc;
  fd_set fds;
  unsigned long id = FD_SETSIZE;

  FD_ZERO(&fds);
  FD_CLR(0, &fds);
  FD_SET(1, &fds);
  int a = FD_ISSET(2, &fds);
  int b = select(4, &fds, 0, 0, &tv);
  int c = pselect(4, &fds, 0, 0, &ts, &xc);
}
