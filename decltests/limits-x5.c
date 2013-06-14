/* SUSv2 additions */
#include <limits.h>

int dummy; /* avoid error for empty source file */

/* http://pubs.opengroup.org/onlinepubs/7908799/xsh/limits.h.html

   These names are only defined if the corresponding parameters are
   compile-time constants on a particular implementation.

   AIO_LISTIO_MAX
   AIO_MAX
   AIO_PRIO_DELTA_MAX
   ARG_MAX
   ATEXIT_MAX
   CHILD_MAX
   DELAYTIMER_MAX
   IOV_MAX
   LOGIN_NAME_MAX
   MQ_OPEN_MAX
   MQ_PRIO_MAX
   OPEN_MAX
   PAGESIZE
   PAGE_SIZE
   PASS_MAX
   PTHREAD_DESTRUCTOR_ITERATIONS
   PTHREAD_KEYS_MAX
   PTHREAD_STACK_MIN
   PTHREAD_THREADS_MAX
   RTSIG_MAX
   SEM_NSEMS_MAX
   SEM_VALUE_MAX
   SIGQUEUE_MAX
   STREAM_MAX
   TIMER_MAX
   TTY_NAME_MAX
   TZNAME_MAX

   These names are only defined if the corresponding parameters are
   invariant among all pathnames supported on a particular
   implementation.

   FILESIZEBITS
   LINK_MAX
   MAX_CANON
   MAX_INPUT
   NAME_MAX
   PATH_MAX
   PIPE_BUF
*/

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
#if !defined RE_DUP_MAX || RE_DUP_MAX < _POSIX2_RE_DUP_MAX
#error "RE_DUP_MAX"
#endif

/* These names are always defined. (ignoring those marked LEGACY) */
#if !defined CHARCLASS_NAME_MAX || CHARCLASS_NAME_MAX <  14
#error "CHARCLASS_NAME_MAX"
#endif
#if !defined NL_ARGMAX || NL_ARGMAX < 9
#error "NL_ARGMAX"
#endif
#if !defined NL_LANGMAX || NL_LANGMAX < 14
#error "NL_LANGMAX"
#endif
#if !defined NL_MSGMAX || NL_MSGMAX < 32767
#error "NL_MSGMAX"
#endif
#if !defined NL_NMAX || NL_NMAX < 1
#error "NL_NMAX"
#endif
#if !defined NL_SETMAX || NL_SETMAX < 255
#error "NL_SETMAX"
#endif
#if !defined NL_TEXTMAX || NL_TEXTMAX < _POSIX2_LINE_MAX
#error "NL_TEXTMAX"
#endif
#if !defined NZERO || NZERO < 20
#error "NZERO"
#endif

/* These names are always defined.  The specification states exact
   values for them, but we treat these as lower / upper bounds, on
   the assumption that later standards may make 'em bigger/smaller
   respectively. */

/* ??? Some of these might not be required in X5base. */

#if !defined _POSIX_CLOCKRES_MIN || _POSIX_CLOCKRES_MIN > 20000000
#error "_POSIX_CLOCKRES_MIN"
#endif

#if !defined _POSIX_AIO_LISTIO_MAX || _POSIX_AIO_LISTIO_MAX < 2
#error "_POSIX_AIO_LISTIO_MAX"
#endif
#if !defined _POSIX_AIO_MAX || _POSIX_AIO_MAX < 1
#error "_POSIX_AIO_MAX"
#endif
#if !defined _POSIX_ARG_MAX || _POSIX_ARG_MAX < 4096
#error "_POSIX_ARG_MAX"
#endif
#if !defined _POSIX_CHILD_MAX || _POSIX_CHILD_MAX < 6
#error "_POSIX_CHILD_MAX"
#endif
#if !defined _POSIX_DELAYTIMER_MAX || _POSIX_DELAYTIMER_MAX < 32
#error "_POSIX_DELAYTIMER_MAX"
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
#if !defined _POSIX_MQ_OPEN_MAX || _POSIX_MQ_OPEN_MAX < 8
#error "_POSIX_MQ_OPEN_MAX"
#endif
#if !defined _POSIX_MQ_PRIO_MAX || _POSIX_MQ_PRIO_MAX < 32
#error "_POSIX_MQ_PRIO_MAX"
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
#if !defined _POSIX_RTSIG_MAX || _POSIX_RTSIG_MAX < 8
#error "_POSIX_RTSIG_MAX"
#endif
#if !defined _POSIX_SEM_NSEMS_MAX || _POSIX_SEM_NSEMS_MAX < 256
#error "_POSIX_SEM_NSEMS_MAX"
#endif
#if !defined _POSIX_SEM_VALUE_MAX || _POSIX_SEM_VALUE_MAX < 32767
#error "_POSIX_SEM_VALUE_MAX"
#endif
#if !defined _POSIX_SIGQUEUE_MAX || _POSIX_SIGQUEUE_MAX < 32
#error "_POSIX_SIGQUEUE_MAX"
#endif
#if !defined _POSIX_SSIZE_MAX || _POSIX_SSIZE_MAX < 32767
#error "_POSIX_SSIZE_MAX"
#endif
#if !defined _POSIX_STREAM_MAX || _POSIX_STREAM_MAX < 8
#error "_POSIX_STREAM_MAX"
#endif
#if !defined _POSIX_THREAD_DESTRUCTOR_ITERATIONS || _POSIX_THREAD_DESTRUCTOR_ITERATIONS < 4
#error "_POSIX_THREAD_DESTRUCTOR_ITERATIONS"
#endif
#if !defined _POSIX_THREAD_KEYS_MAX || _POSIX_THREAD_KEYS_MAX < 128
#error "_POSIX_THREAD_KEYS_MAX"
#endif
#if !defined _POSIX_THREAD_THREADS_MAX || _POSIX_THREAD_THREADS_MAX < 64
#error "_POSIX_THREAD_THREADS_MAX"
#endif
#if !defined _POSIX_TIMER_MAX || _POSIX_TIMER_MAX < 32
#error "_POSIX_TIMER_MAX"
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
#if !defined _POSIX2_COLL_WEIGHTS_MAX || _POSIX2_COLL_WEIGHTS_MAX < 2
#error "_POSIX2_COLL_WEIGHTS_MAX"
#endif
#if !defined _POSIX2_EXPR_NEST_MAX || _POSIX2_EXPR_NEST_MAX < 32
#error "_POSIX2_EXPR_NEST_MAX"
#endif
#if !defined _POSIX2_LINE_MAX || _POSIX2_LINE_MAX < 2048
#error "_POSIX2_LINE_MAX"
#endif
#if !defined _POSIX2_RE_DUP_MAX || _POSIX2_RE_DUP_MAX < 255
#error "_POSIX2_RE_DUP_MAX"
#endif
#if !defined _XOPEN_IOV_MAX || _XOPEN_IOV_MAX < 16
#error "_XOPEN_IOV_MAX"
#endif

/* Additional numeric limits (ignoring those marked LEGACY)  */

#if !defined LONG_BIT || LONG_BIT < 32
#error "LONG_BIT"
#endif

#if !defined WORD_BIT || WORD_BIT < 16
#error "WORD_BIT"
#endif
