/* baseline */
#include <float.h>

/* Note: C89 did not require that any of the following be constant
   expressions (let alone usable in #if), except FLT_RADIX.
   Therefore we do not check minimum-maximums. */

#if FLT_RADIX < 2
#error "FLT_RADIX"
#endif

void f(void)
{
  int _ = FLT_ROUNDS;

  int a = FLT_MANT_DIG;
  int b = DBL_MANT_DIG;
  int c = LDBL_MANT_DIG;

  int d = FLT_MIN_EXP;
  int e = DBL_MIN_EXP;
  int f = LDBL_MIN_EXP;

  int g = FLT_MIN_10_EXP;
  int h = DBL_MIN_10_EXP;
  int i = LDBL_MIN_10_EXP;

  int j = FLT_MAX_EXP;
  int k = DBL_MAX_EXP;
  int l = LDBL_MAX_EXP;

  int m = FLT_MAX_10_EXP;
  int n = DBL_MAX_10_EXP;
  int o = LDBL_MAX_10_EXP;

  float p = FLT_MAX;
  double q = DBL_MAX;
  long double r = LDBL_MAX;

  float s = FLT_MIN;
  double t = DBL_MIN;
  long double u = LDBL_MIN;

  float v = FLT_EPSILON;
  double w = DBL_EPSILON;
  long double x = LDBL_EPSILON;
}
