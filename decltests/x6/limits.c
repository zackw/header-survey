/* limit constants */
#include <limits.h>

/* increased values for old minima */
#if _POSIX_CHILD_MAX < 25
#error "_POSIX_CHILD_MAX"
#endif
#if _POSIX_NGROUPS_MAX < 8
#error "_POSIX_NGROUPS_MAX"
#endif
#if _POSIX_OPEN_MAX < 20
#error "_POSIX_OPEN_MAX"
#endif
#if _POSIX_PATH_MAX < 256
#error "_POSIX_PATH_MAX"
#endif
#if _POSIX_TZNAME_MAX < 6
#error "_POSIX_TZNAME_MAX"
#endif

/* new minima */
#if !defined _POSIX_RE_DUP_MAX || _POSIX_RE_DUP_MAX < 255
#error "_POSIX_RE_DUP_MAX"
#endif
#if !defined _POSIX_SYMLINK_MAX || _POSIX_SYMLINK_MAX < 255
#error "_POSIX_SYMLINK_MAX"
#endif
#if !defined _POSIX_SYMLOOP_MAX || _POSIX_SYMLOOP_MAX < 8
#error "_POSIX_SYMLOOP_MAX"
#endif

/* not necessarily defined */
#if defined RE_DUP_MAX && RE_DUP_MAX < _POSIX_RE_DUP_MAX
#error "RE_DUP_MAX"
#endif
#if defined SYMLINK_MAX && SYMLINK_MAX < _POSIX_SYMLINK_MAX
#error "SYMLINK_MAX"
#endif
#if defined SYMLOOP_MAX && SYMLINK_MAX < _POSIX_SYMLOOP_MAX
#error "SYMLOOP_MAX"
#endif

int dummy; /* avoid error for empty source file */
