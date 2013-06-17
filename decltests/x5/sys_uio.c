#include <sys/uio.h>

void f(int aa, const struct iovec *bb, int cc)
{
  ssize_t a = readv(aa, bb, cc);
  ssize_t b = writev(aa, bb, cc);

  void  *const *c = &bb[0].iov_base;
  const size_t *d = &bb[0].iov_len;
}
