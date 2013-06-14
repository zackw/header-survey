/* baseline */
#define _XOPEN_SOURCE 500
#include <grp.h>

void f(gid_t aa, const char *bb, char *cc, size_t dd)
{
  struct group *ee;
  struct group gg;
  char **gga = &gg->gr_name;
  gid_t *ggb = &gg->gr_gid;
  char ***ggc= &gg->gr_mem;

  struct group *a = getgrgid(aa);
  struct group *b = getgrnam(bb);
  int c = getgrgid_r(aa, &gg, cc, dd, &ee);
  int d = getgrnam_r(bb, &gg, cc, dd, &ee);
  struct group *e = getgrent();
  endgrent();
  setgrent();
}
