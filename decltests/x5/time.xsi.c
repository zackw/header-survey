/* XSI features */
#include <time.h>

void f(void)
{
  struct tm *(*a)(const char *) = getdate;
  char *(*b)(const char *, const char *, struct tm *) = strptime;
  int c = getdate_err;
  int d = daylight;
  long e = timezone;
}
