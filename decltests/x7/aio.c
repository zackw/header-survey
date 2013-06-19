/* types */
#include <aio.h>

void f(void)
{
  off_t a;
  pthread_attr_t b;
  size_t c;
  ssize_t d;
  struct timespec e;
  time_t *es = &e.tv_sec;
  /* tv_nsec is spec'd as bare 'long' but may not actually be that
     type (depending on the ABI), so we just make sure it exists and
     can hold the largest value it's required to hold.  */
  e.tv_nsec = 999999999L;
}

/* this will provoke a warning if 'struct sigevent' isn't declared */
extern void g(struct sigevent *);
