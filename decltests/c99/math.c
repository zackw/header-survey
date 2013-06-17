/* additional C99 functions */
#include <math.h>

void tm(void)
{
  float_t a;
  double_t d;

  float       hugef = HUGE_VALF;
  long double hugel = HUGE_VALL;

  int fpinf    = FP_INFINITE;
  int fpnan    = FP_NAN;
  int fpnor    = FP_NORMAL;
  int fpsub    = FP_SUBNORMAL;
  int fpzer    = FP_ZERO;

  int ilogb0   = FP_ILOGB0;
  int ilogbnan = FP_ILOGBNAN;

  int merrno   = MATH_ERRNO;
  int merrexc  = MATH_ERREXCEPT;
  int merrhdl  = math_errhandling;
}

/* The classification and comparison macros are always type-generic. */
void fc(float a, double aa, long double aaa,
        float b, double bb, long double bbb)
{
  int c = fpclassify(a);
  int cc = fpclassify(aa);
  int ccc = fpclassify(aaa);

  int d = isfinite(a);
  int dd = isfinite(aa);
  int ddd = isfinite(aaa);

  int e = isinf(a);
  int ee = isinf(aa);
  int eee = isinf(aaa);

  int f = isnan(a);
  int ff = isnan(aa);
  int fff = isnan(aaa);

  int g = isnormal(a);
  int gg = isnormal(aa);
  int ggg = isnormal(aaa);

  int h = signbit(a);
  int hh = signbit(aa);
  int hhh = signbit(aaa);

  int i = isgreater(a, b);
  int ii = isgreater(aa, bb);
  int iii = isgreater(aaa, bbb);

  int j = isgreaterequal(a, b);
  int jj = isgreaterequal(aa, bb);
  int jjj = isgreaterequal(aaa, bbb);

  int k = isless(a, b);
  int kk = isless(aa, bb);
  int kkk = isless(aaa, bbb);

  int l = islessequal(a, b);
  int ll = islessequal(aa, bb);
  int lll = islessequal(aaa, bbb);

  int m = islessgreater(a, b);
  int mm = islessgreater(aa, bb);
  int mmm = islessgreater(aaa, bbb);

  int n = isunordered(a, b);
  int nn = isunordered(aa, bb);
  int nnn = isunordered(aaa, bbb);
}

/* Float and long double equivalents of C89 math functions */
void ff(float x, float y)
{
  float a = acosf(x);
  float b = asinf(x);
  float c = atanf(x);
  float d = atan2f(x, y);

  float e = cosf(x);
  float f = sinf(x);
  float g = tanf(x);

  float h = coshf(x);
  float i = sinhf(x);
  float j = tanhf(x);

  float k = expf(x);
  float l = logf(x);
  float m = log10f(x);
  float n = powf(x, y);
  float o = sqrtf(x);

  int ee;
  float ii;
  float p = frexpf(x, &ee);
  float q = ldexpf(y, ee);
  float r = modff(x, &ii);

  float s = ceilf(x);
  float t = fabsf(x);
  float u = floorf(x);
  float v = fmodf(x, y);
}

void fl(long double x, long double y)
{
  long double a = acosl(x);
  long double b = asinl(x);
  long double c = atanl(x);
  long double d = atan2l(x, y);

  long double e = cosl(x);
  long double f = sinl(x);
  long double g = tanl(x);

  long double h = coshl(x);
  long double i = sinhl(x);
  long double j = tanhl(x);

  long double k = expl(x);
  long double l = logl(x);
  long double m = log10l(x);
  long double n = powl(x, y);
  long double o = sqrtl(x);

  int ee;
  long double ii;
  long double p = frexpl(x, &ee);
  long double q = ldexpl(y, ee);
  long double r = modfl(x, &ii);

  long double s = ceill(x);
  long double t = fabsl(x);
  long double u = floorl(x);
  long double v = fmodl(x, y);
}

/* Functions not in C89 */
void gd(double xx, double yy, long double yyy, double zz, int nn, long int nnn)
{
  double a = acosh(xx);
  double b = asinh(xx);
  double c = atanh(xx);

  double d = exp2(xx);
  double e = expm1(xx);
  double f = cbrt(xx);
  double g = hypot(xx, yy);

  int    h = ilogb(xx);
  double i = log1p(xx);
  double j = log2(xx);
  double k = logb(xx);
  double l = scalbn(xx, nn);
  double m = scalbln(xx, nnn);

  double n = erf(xx);
  double o = erfc(xx);
  double p = lgamma(xx);
  double q = tgamma(xx);

  double    r = nearbyint(xx);
  double    s = rint(xx);
  long      t = lrint(xx);
  long long u = llrint(xx);
  double    v = round(xx);
  long      w = lround(xx);
  long long x = llround(xx);
  double    y = trunc(x);
  double    z = remainder(xx, yy);

  int aa;
  double bb = remquo(xx, yy, &aa);
  double cc = copysign(xx, yy);
  double dd = nan("");
  double ee = nextafter(xx, yy);
  double ff = nexttoward(xx, yyy);
  double gg = fdim(xx, yy);
  double hh = fmax(xx, yy);
  double ii = fmin(xx, yy);
  double jj = fma(xx, yy, zz);
}

void gf(float xx, float yy, long double yyy, float zz, int nn, long int nnn)
{
  float a = acoshf(xx);
  float b = asinhf(xx);
  float c = atanhf(xx);

  float d = exp2f(xx);
  float e = expm1f(xx);
  float f = cbrtf(xx);
  float g = hypotf(xx, yy);

  int   h = ilogbf(xx);
  float i = log1pf(xx);
  float j = log2f(xx);
  float k = logbf(xx);
  float l = scalbnf(xx, nn);
  float m = scalblnf(xx, nnn);

  float n = erff(xx);
  float o = erfcf(xx);
  float p = lgammaf(xx);
  float q = tgammaf(xx);

  float     r = nearbyintf(xx);
  float     s = rintf(xx);
  long      t = lrintf(xx);
  long long u = llrintf(xx);
  float     v = roundf(xx);
  long      w = lroundf(xx);
  long long x = llroundf(xx);
  float     y = truncf(x);
  float     z = remainderf(xx, yy);

  int aa;
  float bb = remquof(xx, yy, &aa);
  float cc = copysignf(xx, yy);
  float dd = nanf("");
  float ee = nextafterf(xx, yy);
  float ff = nexttowardf(xx, yyy);
  float gg = fdimf(xx, yy);
  float hh = fmaxf(xx, yy);
  float ii = fminf(xx, yy);
  float jj = fmaf(xx, yy, zz);
}

void gl(long double xx, long double yy, long double zz, int nn, long int nnn)
{
  long double a = acoshl(xx);
  long double b = asinhl(xx);
  long double c = atanhl(xx);

  long double d = exp2l(xx);
  long double e = expm1l(xx);
  long double f = cbrtl(xx);
  long double g = hypotl(xx, yy);

  int         h = ilogbl(xx);
  long double i = log1pl(xx);
  long double j = log2l(xx);
  long double k = logbl(xx);
  long double l = scalbnl(xx, nn);
  long double m = scalblnl(xx, nnn);

  long double n = erfl(xx);
  long double o = erfcl(xx);
  long double p = lgammal(xx);
  long double q = tgammal(xx);

  long double r = nearbyintl(xx);
  long double s = rintl(xx);
  long        t = lrintl(xx);
  long long   u = llrintl(xx);
  long double v = roundl(xx);
  long        w = lroundl(xx);
  long long   x = llroundl(xx);
  long double y = truncl(x);
  long double z = remainderl(xx, yy);

  int aa;
  long double bb = remquol(xx, yy, &aa);
  long double cc = copysignl(xx, yy);
  long double dd = nanl("");
  long double ee = nextafterl(xx, yy);
  long double ff = nexttowardl(xx, yy);
  long double gg = fdiml(xx, yy);
  long double hh = fmaxl(xx, yy);
  long double ii = fminl(xx, yy);
  long double jj = fmal(xx, yy, zz);
}
