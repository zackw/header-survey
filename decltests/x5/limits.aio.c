/* AIO option */
#include <limits.h>

/* minimum-maximum */
#if !defined _POSIX_AIO_LISTIO_MAX || _POSIX_AIO_LISTIO_MAX < 2
#error "_POSIX_AIO_LISTIO_MAX"
#endif
#if !defined _POSIX_AIO_MAX || _POSIX_AIO_MAX < 1
#error "_POSIX_AIO_MAX"
#endif

/* not necessarily defined */
#if defined AIO_LISTIO_MAX && AIO_LISTIO_MAX < _POSIX_AIO_LISTIO_MAX
#error "AIO_LISTIO_MAX"
#endif
#if defined AIO_MAX && AIO_MAX < _POSIX_AIO_MAX
#error "AIO_MAX"
#endif
#if defined AIO_PRIO_DELTA_MAX && AIO_PRIO_DELTA_MAX < 0
#error "AIO_PRIO_DELTA_MAX"
#endif

int dummy; /* avoid error for empty source file */
