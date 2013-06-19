/* <code>select</code> and <code>fd_set</code> manipulation */
#include <sys/time.h>

/* that these are here as well as <sys/select.h> strikes me as a
   historical wart likely to be removed in the future */

void f(void)
{
  fd_set fds;
  /* XPG4.2 does specify the contents of this structure but it is
     better to treat it as opaque. */

  unsigned long id = FD_SETSIZE;

  FD_ZERO(&fds);
  FD_CLR(0, &fds);
  FD_SET(1, &fds);
  int a = FD_ISSET(2, &fds);

  struct timeval tv;
  int e = select(4, &fds, 0, 0, &tv);
}
