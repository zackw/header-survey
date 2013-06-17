#include <mqueue.h>

void f(const char *dd, int ee, mode_t ff, char *gg, size_t hh)
{
  struct mq_attr aa, oaa;
  long *aaf  = &aa.mq_flags;
  long *aama = &aa.mq_maxmsg;
  long *aams = &aa.mq_msgsize;
  long *aac  = &aa.mq_curmsgs;

  struct sigevent bb;
  unsigned int ii;

  mqd_t cc  = mq_open(dd, ee, ff);
  int a     = mq_getattr(cc, &aa);
  int b     = mq_notify(cc, &bb);
  ssize_t c = mq_receive(cc, gg, hh, &ii);
  int d     = mq_send(cc, gg, hh, ii);
  int e     = mq_setattr(cc, &aa, &oaa);
  int f     = mq_close(cc);
  int g     = mq_unlink(dd);
}
