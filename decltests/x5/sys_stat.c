#include <sys/stat.h>

void sstruct(struct stat *st)
{
  dev_t     *a = &st->st_dev;
  ino_t     *b = &st->st_ino;
  mode_t    *c = &st->st_mode;
  nlink_t   *d = &st->st_nlink;
  uid_t     *e = &st->st_uid;
  gid_t     *f = &st->st_gid;
  off_t     *h = &st->st_size;
  time_t    *i = &st->st_atime;
  time_t    *j = &st->st_mtime;
  time_t    *k = &st->st_ctime;
}

void smacros(struct stat *aa)
{
  int
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
    sy = S_ISGID;

  int a = S_ISBLK(aa->st_mode);
  int b = S_ISCHR(aa->st_mode);
  int c = S_ISDIR(aa->st_mode);
  int d = S_ISFIFO(aa->st_mode);
  int e = S_ISREG(aa->st_mode);
  int f = S_ISLNK(aa->st_mode);
}

void f(const char *aa, mode_t bb, int dd)
{
  struct stat ee;

  int a = chmod(aa, bb);
  int b = fchmod(dd, bb);
  int c = fstat(dd, &ee);
  int e = mkdir(aa, bb);
  int f = mkfifo(aa, bb);
  int h = stat(aa, &ee);
  mode_t i = umask(bb);
}
