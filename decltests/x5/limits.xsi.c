/* XSI: limit constants */
#include <limits.h>

/* minimum-maximum */
#if !defined _XOPEN_IOV_MAX || _XOPEN_IOV_MAX < 16
#error "_XOPEN_IOV_MAX"
#endif

/* not necessarily defined */
#if defined IOV_MAX && IOV_MAX < _XOPEN_IOV_MAX
#error "IOV_MAX"
#endif

/* required */
#if !defined NL_ARGMAX || NL_ARGMAX < 9
#error "NL_ARGMAX"
#endif
#if !defined NL_LANGMAX || NL_LANGMAX < 14
#error "NL_LANGMAX"
#endif
#if !defined NL_MSGMAX || NL_MSGMAX < 32767
#error "NL_MSGMAX"
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

int dummy; /* avoid error for empty source file */
