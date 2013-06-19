#include <ftw.h>

int cc[] = {
  FTW_F,
  FTW_D,
  FTW_DNR,
  FTW_DP,
  FTW_NS,
  FTW_SL,
  FTW_SLN,
  FTW_PHYS,
  FTW_MOUNT,
  FTW_DEPTH,
  FTW_CHDIR,
};

/* ftw() obsolescent in Issue 7
int cb_ftw(const char *p,
           const struct stat *s,
           int f)
{
  return 0;
}
*/

int cb_nftw(const char *p,
            const struct stat *s,
            int f,
            struct FTW *w)
{
  return 0;
}

void f(void)
{
  /*int l = ftw("path", cb_ftw, 10);*/
  int m = nftw("path", cb_nftw, 10, 0);
}

/* XSI, Issue 6/7 macros excluded from this copy */
void smacros(struct stat *aa)
{
  struct stat s_; /* confirm complete type */
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
