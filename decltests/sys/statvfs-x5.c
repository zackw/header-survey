/* baseline */
#include <sys/statvfs.h>

void f(int aa, const char *bb)
{
  struct statvfs f;
  int a = fstatvfs(aa, &f);
  int b = statvfs(bb, &f);

  unsigned long *c = &f.f_bsize;
  unsigned long *d = &f.f_frsize;
  fsblkcnt_t    *e = &f.f_blocks;
  fsblkcnt_t    *g = &f.f_bfree;
  fsblkcnt_t    *h = &f.f_bavail;
  fsfilcnt_t    *i = &f.f_files;
  fsfilcnt_t    *j = &f.f_ffree;
  fsfilcnt_t    *k = &f.f_favail;
  unsigned long *l = &f.f_fsid;
  unsigned long *m = &f.f_flag;
  unsigned long *n = &f.f_namemax;

  int o = ST_RDONLY;
  int p = ST_NOSUID;
}
