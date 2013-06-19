/* optional: limit constants for semaphores */
#include <limits.h>

/* minimum-maximum */
#if !defined _POSIX_SEM_NSEMS_MAX || _POSIX_SEM_NSEMS_MAX < 256
#error "_POSIX_SEM_NSEMS_MAX"
#endif
#if !defined _POSIX_SEM_VALUE_MAX || _POSIX_SEM_VALUE_MAX < 32767
#error "_POSIX_SEM_VALUE_MAX"
#endif

/* not necessarily defined */
#if defined SEM_NSEMS_MAX && SEM_NSEMS_MAX < _POSIX_SEM_NSEMS_MAX
#error "SEM_NSEMS_MAX"
#endif
#if defined SEM_VALUE_MAX && SEM_VALUE_MAX < _POSIX_SEM_VALUE_MAX
#error "SEM_VALUE_MAX"
#endif

int dummy; /* avoid error for empty source file */
