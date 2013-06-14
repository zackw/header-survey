/* baseline */
#include <time.h>

void ty(void)
{
  char *a = NULL;
  clock_t b = CLOCKS_PER_SEC;
  size_t c;
  time_t d;
  static struct tm tm; /* static so reads below are not uninitialized */

  /* C89 and C99 specify that all of these have type 'int', but an
     implementation might reasonably pick a different type for some of
     them, whether to save space (sec, min, hour, mday, mon, wday,
     isdst are all packable into 'unsigned char', and yday would fit
     into a 9-bit bitfield) or to extend the range (a 64-bit
     second-counting time_t can reach well past Gregorian year
     2,147,485,547) so we don't aggressively validate that as we do
     for e.g. ldiv_t. */
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
