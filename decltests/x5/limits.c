/* limit constants */
#include <limits.h>

/* Removed in Issue 6 or 7:
   PASS_MAX, TMP_MAX, NL_NMAX, _POSIX2_RE_DUP_MAX */

/* minimum-maximum */
#if !defined _POSIX_ARG_MAX || _POSIX_ARG_MAX < 4096
#error "_POSIX_ARG_MAX"
#endif
#if !defined _POSIX_CHILD_MAX || _POSIX_CHILD_MAX < 6
#error "_POSIX_CHILD_MAX"
#endif
#if !defined _POSIX_HOST_NAME_MAX || _POSIX_HOST_NAME_MAX < 255
#error "_POSIX_HOST_NAME_MAX"
#endif
#if !defined _POSIX_LINK_MAX || _POSIX_LINK_MAX < 8
#error "_POSIX_LINK_MAX"
#endif
#if !defined _POSIX_LOGIN_NAME_MAX || _POSIX_LOGIN_NAME_MAX < 9
#error "_POSIX_LOGIN_NAME_MAX"
#endif
#if !defined _POSIX_MAX_CANON || _POSIX_MAX_CANON < 255
#error "_POSIX_MAX_CANON"
#endif
#if !defined _POSIX_MAX_INPUT || _POSIX_MAX_INPUT < 255
#error "_POSIX_MAX_INPUT"
#endif
#if !defined _POSIX_NAME_MAX || _POSIX_NAME_MAX < 14
#error "_POSIX_NAME_MAX"
#endif
#if !defined _POSIX_NGROUPS_MAX || _POSIX_NGROUPS_MAX < 0
#error "_POSIX_NGROUPS_MAX"
#endif
#if !defined _POSIX_OPEN_MAX || _POSIX_OPEN_MAX < 16
#error "_POSIX_OPEN_MAX"
#endif
#if !defined _POSIX_PATH_MAX || _POSIX_PATH_MAX < 255
#error "_POSIX_PATH_MAX"
#endif
#if !defined _POSIX_PIPE_BUF || _POSIX_PIPE_BUF < 512
#error "_POSIX_PIPE_BUF"
#endif
#if !defined _POSIX_SSIZE_MAX || _POSIX_SSIZE_MAX < 32767
#error "_POSIX_SSIZE_MAX"
#endif
#if !defined _POSIX_STREAM_MAX || _POSIX_STREAM_MAX < 8
#error "_POSIX_STREAM_MAX"
#endif
#if !defined _POSIX_TTY_NAME_MAX || _POSIX_TTY_NAME_MAX < 9
#error "_POSIX_TTY_NAME_MAX"
#endif
#if !defined _POSIX_TZNAME_MAX || _POSIX_TZNAME_MAX < 3
#error "_POSIX_TZNAME_MAX"
#endif

#if !defined _POSIX2_BC_BASE_MAX || _POSIX2_BC_BASE_MAX < 99
#error "_POSIX2_BC_BASE_MAX"
#endif
#if !defined _POSIX2_BC_DIM_MAX || _POSIX2_BC_DIM_MAX < 2048
#error "_POSIX2_BC_DIM_MAX"
#endif
#if !defined _POSIX2_BC_SCALE_MAX || _POSIX2_BC_SCALE_MAX < 99
#error "_POSIX2_BC_SCALE_MAX"
#endif
#if !defined _POSIX2_BC_STRING_MAX || _POSIX2_BC_STRING_MAX < 1000
#error "_POSIX2_BC_STRING_MAX"
#endif
#if !defined _POSIX2_CHARCLASS_NAME_MAX || _POSIX2_CHARCLASS_NAME_MAX < 14
#error "_POSIX2_CHARCLASS_NAME_MAX"
#endif
#if !defined _POSIX2_COLL_WEIGHTS_MAX || _POSIX2_COLL_WEIGHTS_MAX < 2
#error "_POSIX2_COLL_WEIGHTS_MAX"
#endif
#if !defined _POSIX2_EXPR_NEST_MAX || _POSIX2_EXPR_NEST_MAX < 32
#error "_POSIX2_EXPR_NEST_MAX"
#endif
#if !defined _POSIX2_LINE_MAX || _POSIX2_LINE_MAX < 2048
#error "_POSIX2_LINE_MAX"
#endif

/* not necessarily defined */
#if defined ARG_MAX && ARG_MAX < _POSIX_ARG_MAX
#error "ARG_MAX"
#endif
#if defined ATEXIT_MAX && ATEXIT_MAX < 32
#error "ATEXIT_MAX"
#endif
#if defined CHILD_MAX && CHILD_MAX < _POSIX_CHILD_MAX
#error "CHILD_MAX"
#endif
#if defined HOST_NAME_MAX && HOST_NAME_MAX < _POSIX_HOST_NAME_MAX
#error "HOST_NAME_MAX"
#endif
#if defined LOGIN_NAME_MAX && LOGIN_NAME_MAX < _POSIX_LOGIN_NAME_MAX
#error "LOGIN_NAME_MAX"
#endif
#if defined OPEN_MAX && OPEN_MAX < _POSIX_OPEN_MAX
#error "OPEN_MAX"
#endif
#if defined PAGESIZE && PAGESIZE < 1
#error "PAGESIZE"
#endif
#if defined PAGE_SIZE && PAGE_SIZE < 1
#error "PAGE_SIZE"
#endif
#if defined PAGESIZE && defined PAGE_SIZE && PAGESIZE != PAGE_SIZE
#error "PAGESIZE != PAGE_SIZE"
#endif
#if defined STREAM_MAX && STREAM_MAX < _POSIX_STREAM_MAX
#error "STREAM_MAX"
#endif
#if defined TTY_NAME_MAX && TTY_NAME_MAX < _POSIX_TTY_NAME_MAX
#error "TTY_NAME_MAX"
#endif
#if defined TZNAME_MAX && TZNAME_MAX < _POSIX_TZNAME_MAX
#error "TZNAME_MAX"
#endif

/* These names are only defined if the corresponding parameters are
   invariant among all pathnames supported on a particular
   implementation. */

#if defined FILESIZEBITS && FILESIZEBITS < 32
#error "FILESIZEBITS"
#endif
#if defined LINK_MAX && LINK_MAX < _POSIX_LINK_MAX
#error "LINK_MAX"
#endif
#if defined MAX_CANON && MAX_CANON < _POSIX_MAX_CANON
#error "MAX_CANON"
#endif
#if defined MAX_INPUT && MAX_INPUT < _POSIX_MAX_INPUT
#error "MAX_INPUT"
#endif
#if defined NAME_MAX && NAME_MAX < _POSIX_NAME_MAX
#error "NAME_MAX"
#endif
#if defined PATH_MAX && PATH_MAX < _POSIX_PATH_MAX
#error "PATH_MAX"
#endif
#if defined PIPE_BUF && PIPE_BUF < _POSIX_PIPE_BUF
#error "PIPE_BUF"
#endif


/* These names are always defined, but the runtime value may be larger
   than the value known at compile time. */

#if !defined BC_BASE_MAX || BC_BASE_MAX < _POSIX2_BC_BASE_MAX
#error "BC_BASE_MAX"
#endif
#if !defined BC_DIM_MAX || BC_DIM_MAX < _POSIX2_BC_DIM_MAX
#error "BC_DIM_MAX"
#endif
#if !defined BC_SCALE_MAX || BC_SCALE_MAX < _POSIX2_BC_SCALE_MAX
#error "BC_SCALE_MAX"
#endif
#if !defined BC_STRING_MAX || BC_STRING_MAX < _POSIX2_BC_STRING_MAX
#error "BC_STRING_MAX"
#endif
#if !defined CHARCLASS_NAME_MAX || CHARCLASS_NAME_MAX < _POSIX2_CHARCLASS_NAME_MAX
#error "CHARCLASS_NAME_MAX"
#endif
#if !defined COLL_WEIGHTS_MAX || COLL_WEIGHTS_MAX < _POSIX2_COLL_WEIGHTS_MAX
#error "COLL_WEIGHTS_MAX"
#endif
#if !defined EXPR_NEST_MAX || EXPR_NEST_MAX < _POSIX2_EXPR_NEST_MAX
#error "EXPR_NEST_MAX"
#endif
#if !defined LINE_MAX || LINE_MAX < _POSIX2_LINE_MAX
#error "LINE_MAX"
#endif
#if !defined NGROUPS_MAX || NGROUPS_MAX < 8
#error "NGROUPS_MAX"
#endif

/* Additional numeric limits (ignoring those marked LEGACY)  */
#if !defined LONG_BIT || LONG_BIT < 32
#error "LONG_BIT"
#endif

#if !defined WORD_BIT || WORD_BIT < 16
#error "WORD_BIT"
#endif

#if !defined SSIZE_MAX || SSIZE_MAX < _POSIX_SSIZE_MAX
#error "SSIZE_MAX"
#endif

int dummy; /* avoid error for empty source file */
