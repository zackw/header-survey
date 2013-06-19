/* optional: timer support */
#include <time.h>

clockid_t xx[] = {
  CLOCK_PROCESS_CPUTIME_ID,
  CLOCK_THREAD_CPUTIME_ID,
};
