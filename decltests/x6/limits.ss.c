/* optional: limit constants for sporadic scheduling */
#include <limits.h>

#if !defined _POSIX_SS_REPL_MAX || _POSIX_SS_REPL_MAX < 4
#error "_POSIX_SS_REPL_MAX"
#endif
#if defined SS_REPL_MAX && SS_REPL_MAX < _POSIX_SS_REPL_MAX
#error "_POSIX_SS_REPL_MAX"
#endif

int dummy; /* avoid error for empty source file */
