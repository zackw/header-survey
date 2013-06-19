/* timeouts option */
#include <mqueue.h>

void f(mqd_t aa, char *bb, const char *cc, size_t dd,
       unsigned *ee, const struct timespec *ff)
{
  ssize_t a = mq_timedreceive(aa, bb, dd, ee, ff);
  int     b = mq_timedsend(aa, cc, dd, *ee, ff);
}
