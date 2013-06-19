/* optional: limit constants for timers */
#include <limits.h>

/* minimum-maximum */
#if !defined _POSIX_CLOCKRES_MIN || _POSIX_CLOCKRES_MIN > 20000000
#error "_POSIX_CLOCKRES_MIN"
#endif
#if !defined _POSIX_DELAYTIMER_MAX || _POSIX_DELAYTIMER_MAX < 32
#error "_POSIX_DELAYTIMER_MAX"
#endif
#if !defined _POSIX_TIMER_MAX || _POSIX_TIMER_MAX < 32
#error "_POSIX_TIMER_MAX"
#endif

/* not necessarily defined */
#if defined DELAYTIMER_MAX && DELAYTIMER_MAX < _POSIX_DELAYTIMER_MAX
#error "DELAYTIMER_MAX"
#endif
#if defined TIMER_MAX && TIMER_MAX < _POSIX_TIMER_MAX
#error "TIMER_MAX"
#endif

int dummy; /* avoid error for empty source file */
