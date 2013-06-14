/* baseline */
#include <limits.h>

/* "The values given below shall be replaced by constant expressions
   suitable for use in #if directives...Their implementation-defined
   values shall be equal or greater in magnitude (absolute value) to
   those given below, with the same sign." */

/* C89 requires that #if do its calculations in [unsigned] long.
   Therefore, we only need to worry about signedness on the constants
   for [U]LONG_(MIN|MAX), but we annotate everything properly anyway. */

#if CHAR_BIT < 8
#error "CHAR_BIT"
#endif

#if MB_LEN_MAX < 1
#error "MB_LEN_MAX"
#endif

#if SCHAR_MIN > -127
#error "SCHAR_MIN"
#endif
#if SCHAR_MAX <  127
#error "SCHAR_MAX"
#endif
#if UCHAR_MAX <  255U
#error "UCHAR_MAX"
#endif

#if CHAR_MIN != SCHAR_MIN && CHAR_MIN != UCHAR_MIN
#error "CHAR_MIN"
#endif
#if CHAR_MAX != SCHAR_MAX && CHAR_MAX != UCHAR_MAX
#error "CHAR_MAX"
#endif

#if SHRT_MIN > -32767
#error "SHRT_MIN"
#endif
#if SHRT_MAX <  32767
#error "SHRT_MAX"
#endif
#if USHRT_MAX < 65535U
#error "USHRT_MAX"
#endif

#if INT_MIN > -32767
#error "INT_MIN"
#endif
#if INT_MAX <  32767
#error "INT_MAX"
#endif
#if UINT_MAX < 65535U
#error "UINT_MAX"
#endif

#if LONG_MIN > -2147483647L
#error "LONG_MIN"
#endif
#if LONG_MAX <  2147483647L
#error "LONG_MAX"
#endif
#if ULONG_MAX < 4294967295UL
#error "ULONG_MAX"
#endif

int dummy; /* avoid error for empty source file */
