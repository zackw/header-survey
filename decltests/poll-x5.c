/* baseline */
#include <poll.h>

void f(void)
{
  struct pollfd pf;
  int *pff = &pf.fd;
  short *pfe = &pf.events;
  short *pfr = &pf.revents;
  nfds_t nf = 1;

  short
    a = POLLIN,
    b = POLLRDNORM,
    c = POLLRDBAND,
    d = POLLPRI,
    e = POLLOUT,
    f = POLLWRNORM,
    g = POLLWRBAND,
    h = POLLERR,
    i = POLLHUP,
    j = POLLNVAL;

  int k = poll(&pf, nf, 0);
}
