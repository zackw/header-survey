#include <sys/times.h>

/* This is arguably obsoleted by getrusage(), but it's not officially
   marked as such, and it's in some ways more convenient. */

void f(void)
{
  struct tms tms;
  clock_t a = times(&tms);
  clock_t *b = &tms.tms_utime;
  clock_t *c = &tms.tms_stime;
  clock_t *d = &tms.tms_cutime;
  clock_t *e = &tms.tms_cstime;
}
