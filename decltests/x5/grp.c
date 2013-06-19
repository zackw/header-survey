#include <grp.h>

void f(void)
{
  struct group gg;
  char **gga = &gg.gr_name;
  gid_t *ggb = &gg.gr_gid;
  char ***ggc= &gg.gr_mem;
}

struct group *(*a)(gid_t) = getgrgid;
struct group *(*b)(const char *) = getgrnam;
