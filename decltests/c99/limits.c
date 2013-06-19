/* limit constants */
#include <limits.h>

/* "The values given below shall be replaced by constant expressions
   suitable for use in #if directives...Their implementation-defined
   values shall be equal or greater in magnitude (absolute value) to
   those given below, with the same sign." */

/* C99 widens all arithmetic in #if to [u]intmax_t, so the comparisons
   below are safe even if long long is bigger than long. */

#if LLONG_MIN > -9223372036854775807LL
#error "LLONG_MIN"
#endif
#if LLONG_MAX <  9223372036854775807LL
#error "LLONG_MAX"
#endif
#if ULLONG_MAX < 18446744073709551615ULL
#error "ULLONG_MAX"
#endif

int dummy; /* avoid error for empty source file */
