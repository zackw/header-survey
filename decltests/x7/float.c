/* features */
#include <float.h>

/* "Additionally, FLT_MAX_EXP shall be at least as large as
   FLT_MANT_DIG, DBL_MAX_EXP shall be at least as large as
   DBL_MANT_DIG, and LDBL_MAX_EXP shall be at least as large as
   LDBL_MANT_DIG; which has the effect that FLT_MAX, DBL_MAX, and
   LDBL_MAX are integral." */

#if FLT_MAX_EXP < FLT_MANT_DIG
#error "exponent range of `float` is too small"
#endif
#if DBL_MAX_EXP < DBL_MANT_DIG
#error "exponent range of `double` is too small"
#endif
#if LDBL_MAX_EXP < LDBL_MANT_DIG
#error "exponent range of `long double` is too small"
#endif

int dummy; /* avoid error for empty source file */
