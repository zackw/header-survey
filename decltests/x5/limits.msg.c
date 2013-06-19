/* message queue option */
#include <limits.h>

/* minimum-maximum */
#if !defined _POSIX_MQ_OPEN_MAX || _POSIX_MQ_OPEN_MAX < 8
#error "_POSIX_MQ_OPEN_MAX"
#endif
#if !defined _POSIX_MQ_PRIO_MAX || _POSIX_MQ_PRIO_MAX < 32
#error "_POSIX_MQ_PRIO_MAX"
#endif

/* not necessarily defined */
#if defined MQ_OPEN_MAX && MQ_OPEN_MAX < _POSIX_MQ_OPEN_MAX
#error "MQ_OPEN_MAX"
#endif
#if defined MQ_PRIO_MAX && MQ_PRIO_MAX < _POSIX_MQ_PRIO_MAX
#error "MQ_PRIO_MAX"
#endif

int dummy; /* avoid error for empty source file */
