/* XSI constants */
#include <limits.h>

#if !defined _XOPEN_NAME_MAX || _XOPEN_NAME_MAX < 255
#error "_XOPEN_NAME_MAX"
#endif
#if !defined _XOPEN_PATH_MAX || _XOPEN_PATH_MAX < 255
#error "_XOPEN_PATH_MAX"
#endif

#if defined NAME_MAX && NAME_MAX < _XOPEN_NAME_MAX
#error "NAME_MAX"
#endif
#if defined PATH_MAX && PATH_MAX < _XOPEN_PATH_MAX
#error "PATH_MAX"
#endif

int dummy; /* avoid error for empty source file */
