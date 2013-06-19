/* limit constants */
#include <float.h>

/* New constants in C99. */

#ifndef FLT_EVAL_METHOD
#error "FLT_EVAL_METHOD"
#endif

#if DECIMAL_DIG < 10
#error "DECIMAL_DIG"
#endif

#if FLT_DIG < 6
#error "FLT_DIG"
#endif
#if DBL_DIG < 10
#error "DBL_DIG"
#endif
#if LDBL_DIG < 10
#error "LDBL_DIG"
#endif


/* C99 *does* require that all integer values (except FLT_ROUNDS) be
   constants usable in #if, and that all floating-point values be
   compile-time constant expressions. Recheck everything whose status
   has changed.  */

#ifndef FLT_MANT_DIG
#error "FLT_MANT_DIG"
#endif
#ifndef DBL_MANT_DIG
#error "DBL_MANT_DIG"
#endif
#ifndef LDBL_MANT_DIG
#error "LDBL_MANT_DIG"
#endif

#ifndef FLT_MIN_EXP
#error "FLT_MIN_EXP"
#endif
#ifndef DBL_MIN_EXP
#error "DBL_MIN_EXP"
#endif
#ifndef LDBL_MIN_EXP
#error "LDBL_MIN_EXP"
#endif

#ifndef FLT_MAX_EXP
#error "FLT_MAX_EXP"
#endif
#ifndef DBL_MAX_EXP
#error "DBL_MAX_EXP"
#endif
#ifndef LDBL_MAX_EXP
#error "LDBL_MAX_EXP"
#endif

#if FLT_MIN_10_EXP > -37
#error "FLT_MIN_10_EXP"
#endif
#if DBL_MIN_10_EXP > -37
#error "DBL_MIN_10_EXP"
#endif
#if LDBL_MIN_10_EXP > -37
#error "LDBL_MIN_10_EXP"
#endif

#if FLT_MAX_10_EXP < 37
#error "FLT_MAX_10_EXP"
#endif
#if DBL_MAX_10_EXP < 37
#error "DBL_MAX_10_EXP"
#endif
#if LDBL_MAX_10_EXP < 37
#error "LDBL_MAX_10_EXP"
#endif


static const float p = FLT_MAX;
static const double q = DBL_MAX;
static const long double r = LDBL_MAX;

static const float s = FLT_MIN;
static const double t = DBL_MIN;
static const long double u = LDBL_MIN;

static const float v = FLT_EPSILON;
static const double w = DBL_EPSILON;
static const long double x = LDBL_EPSILON;
