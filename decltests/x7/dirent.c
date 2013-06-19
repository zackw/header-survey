/* additional POSIX.1-2008 functions */
#include <dirent.h>

extern int filter(const struct dirent *);

void f(DIR *aa, int bb, const char *cc)
{
  int (*x)(const struct dirent *) = filter;
  int (*xx)(const struct dirent **, const struct dirent **) = alphasort;

  int a  = dirfd(aa);
  DIR *b = fdopendir(bb);

  struct dirent **dd;
  int c = scandir(cc, &dd, x, xx);
}
