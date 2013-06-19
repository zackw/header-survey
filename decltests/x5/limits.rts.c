/* realtime signals option */
#include <limits.h>

/* minimum-maximum */
#if !defined _POSIX_RTSIG_MAX || _POSIX_RTSIG_MAX < 8
#error "_POSIX_RTSIG_MAX"
#endif
#if !defined _POSIX_SIGQUEUE_MAX || _POSIX_SIGQUEUE_MAX < 32
#error "_POSIX_SIGQUEUE_MAX"
#endif

/* not necessarily defined */
#if defined RTSIG_MAX && RTSIG_MAX < _POSIX_RTSIG_MAX
#error "RTSIG_MAX"
#endif
#if defined SIGQUEUE_MAX && SIGQUEUE_MAX < _POSIX_SIGQUEUE_MAX
#error "SIGQUEUE_MAX"
#endif

int dummy; /* avoid error for empty source file */
