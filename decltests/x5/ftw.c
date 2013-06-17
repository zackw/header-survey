#include <ftw.h>

int cb_ftw(const char *p,
           const struct stat *s,
           int f)
{
  return 0;
}

int cb_nftw(const char *p,
            const struct stat *s,
            int f,
            struct FTW *w)
{
  return 0;
}

void f(void)
{
  struct stat st; /* confirm complete type */
  int
    a = FTW_F,
    b = FTW_D,
    c = FTW_DNR,
    d = FTW_DP,
    e = FTW_NS,
    f = FTW_SL,
    g = FTW_SLN,
    h = FTW_PHYS,
    i = FTW_MOUNT,
    j = FTW_DEPTH,
    k = FTW_CHDIR;


  int l = ftw("path", cb_ftw, 10);
  int m = nftw("path", cb_nftw, 10, 0);
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
