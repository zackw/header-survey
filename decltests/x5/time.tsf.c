/* optional: thread-safe functions */
#include <time.h>

void f(void)
{
  char      *(*a)(const struct tm *, char *)   = asctime_r;
  char      *(*b)(const time_t *, char *)      = ctime_r;
  struct tm *(*c)(const time_t *, struct tm *) = gmtime_r;
  struct tm *(*d)(const time_t *, struct tm *) = localtime_r;
}
