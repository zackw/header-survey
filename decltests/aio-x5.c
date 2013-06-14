/* baseline */
#include <aio.h>

void t(struct aiocb *a)
{
  int             *b = &a->aio_fildes;
  off_t           *c = &a->aio_offset;
  volatile void   *d = &a->aio_buf;
  size_t          *e = &a->aio_nbytes;
  int             *f = &a->aio_reqprio;
  struct sigevent *g = &a->aio_sigevent;
  int             *h = &a->aio_lio_opcode;

  int
    c1 = AIO_CANCELED,
    c2 = AIO_NOTCANCELED,
    c3 = AIO_ALLDONE,
    c4 = LIO_WAIT,
    c5 = LIO_NOWAIT,
    c6 = LIO_READ,
    c7 = LIO_WRITE,
    c8 = LIO_NOP;
}

void f(int aa, int bb, struct aiocb *cc, struct aiocb *const *dd,
       const struct aiocb *const *ee,
       const struct timespec *ff, struct sigevent *gg)
{
  int a     = aio_cancel(aa, cc);
  int b     = aio_error(cc);
  int c     = aio_fsync(aa, cc);
  int d     = aio_read(cc);
  ssize_t e = aio_return(cc);
  int f     = aio_suspend(ee, aa, ff);
  int g     = aio_write(cc);
  int h     = lio_listio(aa, dd, bb, gg);
}
