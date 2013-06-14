/* baseline */
#include <sys/stat.h>

void sstruct(struct stat *st)
{
  dev_t     *a = &st->st_dev;
  ino_t     *b = &st->st_ino;
  mode_t    *c = &st->st_mode;
  nlink_t   *d = &st->st_nlink;
  uid_t     *e = &st->st_uid;
  gid_t     *f = &st->st_gid;
  dev_t     *g = &st->st_rdev;
  off_t     *h = &st->st_size;
  time_t    *i = &st->st_atime;
  time_t    *j = &st->st_mtime;
  time_t    *k = &st->st_ctime;
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

    sh = S_IRWXU,
    si = S_IRUSR,
    sj = S_IWUSR,
    sk = S_IXUSR,

    sl = S_IRWXG,
    sm = S_IRGRP,
    sn = S_IWGRP,
    so = S_IXGRP,

    st = S_IRWXO,
    su = S_IROTH,
    sv = S_IWOTH,
    sw = S_IXOTH,

    sx = S_ISUID,
    sy = S_ISGID,
    sz = S_ISVTX;

  int a = S_ISBLK(aa->st_mode);
  int b = S_ISCHR(aa->st_mode);
  int c = S_ISDIR(aa->st_mode);
  int d = S_ISFIFO(aa->st_mode);
  int e = S_ISREG(aa->st_mode);
  int f = S_ISLNK(aa->st_mode);
  int g = S_TYPEISMQ(aa);
  int h = S_TYPEISSEM(aa);
  int i = S_TYPEISSHM(aa);
}

void f(const char *aa, mode_t bb, dev_t cc, int dd)
{
  struct stat ee;

  int a = chmod(aa, bb);
  int b = fchmod(dd, bb);
  int c = fstat(dd, &ee);
  int d = lstat(aa, &ee);
  int e = mkdir(aa, bb);
  int f = mkfifo(aa, bb);
  int g = mknod(aa, bb, cc);
  int h = stat(aa, &ee);
  mode_t i = umask(bb);
}
