/* features */
#include <sys/stat.h>

void f(void)
{
  int (*a)(int, const struct timespec [2]) = futimens;
  int (*b)(int, const char *, const struct timespec [2], int) = utimensat;

  int (*c)(int, const char *, mode_t, int) = fchmodat;
  int (*d)(int, const char *, struct stat *, int) = fstatat;
  int (*e)(int, const char *, mode_t) = mkdirat;
  int (*f)(int, const char *, mode_t) = mkfifoat;

  struct timespec g;
  g.tv_nsec = UTIME_NOW;
  g.tv_nsec = UTIME_OMIT;
}
