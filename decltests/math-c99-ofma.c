/* C99 optional: fused multiply and add */
#include <math.h>

/* These are optionally defined; they reveal the performance
   characteristics of fma(), fmaf(), fmal() to application code. */
#ifndef FP_FAST_FMA
#error "fma() is not fast"
#endif
#ifndef FP_FAST_FMAF
#error "fmaf() is not fast"
#endif
#ifndef FP_FAST_FMAL
#error "fmal() is not fast"
#endif
