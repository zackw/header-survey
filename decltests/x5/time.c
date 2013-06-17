/* additional POSIX+XSI functions */
#include <time.h>

void f(const struct tm *gg, time_t hh, const char *ii, struct sigevent *jj)
{
  clockid_t aa = CLOCK_REALTIME;
  /* CLK_TCK skipped, legacy */

  struct timespec cc;
  time_t *ccs = &cc.tv_sec;
  /* tv_nsec is spec'd as bare 'long' but may not actually be that
     type (depending on the ABI), so we just make sure it exists and
     can hold the largest value it's required to hold.  */
  cc.tv_nsec = 999999999L;

  struct itimerspec dd;
  struct timespec *ddi = &dd.it_interval;
  struct timespec *ddv = &dd.it_value;

  char ee[256];
  struct tm ff;

  char *a = asctime_r(gg, ee);
  char *b = ctime_r(&hh, ee);
  struct tm *c = gmtime_r(&hh, &ff);
  struct tm *d = localtime_r(&hh, &ff);
  char *e = strptime(ii, "%x %X", &ff);
  struct tm *f = getdate(ii);
  int g = getdate_err;

  struct timespec h;
  int i = clock_getres(aa, &h);
  int j = clock_gettime(aa, &h);
  int k = clock_settime(aa, &h);

  timer_t l;
  struct itimerspec m, n;
  int o = timer_create(aa, jj, &l);
  int p = timer_delete(l);
  int q = timer_gettime(l, &m);
  int r = timer_getoverrun(l);
  int s = timer_settime(l, TIMER_ABSTIME, &n, &m);

  struct timespec t, u;
  int v = nanosleep(&t, &u);

  tzset();
  int w = daylight;
  long int x = timezone;
  char **y = tzname;
}
