/* baseline */
#include <time.h>

void ty(void)
{
  char *a = NULL;
  clock_t b = CLOCKS_PER_SEC;
  size_t c;
  time_t d;
  static struct tm tm; /* static so reads below are not uninitialized */

  int e = tm.tm_sec;
  int f = tm.tm_min;
  int g = tm.tm_hour;
  int h = tm.tm_mday;
  int i = tm.tm_mon;
  int j = tm.tm_year;
  int k = tm.tm_wday;
  int l = tm.tm_yday;
  int m = tm.tm_isdst;
}

void f(time_t aa, time_t bb, struct tm *cc)
{
  clock_t a    = clock();
  double b     = difftime(aa, bb);
  time_t c     = mktime(cc);
  time_t d;
  time_t e     = time(&d);
  char *f      = asctime(cc);
  char *g      = ctime(&aa);
  struct tm *h = gmtime(&aa);
  struct tm *i = localtime(&aa);
  char buf[256];
  size_t j     = strftime(buf, 256, "%Y%m%dT%H%M%SZ", h);
}
