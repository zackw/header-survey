/* features */
#include <sys/stat.h>

void smacros(struct stat *aa)
{
  int a = S_ISSOCK(aa->st_mode);
}
