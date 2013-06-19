/* XSI: features */
#include <sys/stat.h>

void sstruct(struct stat *st)
{
  dev_t     *g = &st->st_rdev;
  blksize_t *l = &st->st_blksize;
  blkcnt_t  *m = &st->st_blocks;
}

void smacros(struct stat *aa)
{
  int
    sa = S_IFMT,
    sb = S_IFBLK,
    sc = S_IFCHR,
    sd = S_IFIFO,
    se = S_IFREG,
    sf = S_IFDIR,
    sg = S_IFLNK,
    sz = S_ISVTX;

  int g = S_TYPEISMQ(aa);
  int h = S_TYPEISSEM(aa);
  int i = S_TYPEISSHM(aa);
}

void f(const char *aa, mode_t bb, dev_t cc)
{
  struct stat ee;

  int d = lstat(aa, &ee);
  int g = mknod(aa, bb, cc);
}
