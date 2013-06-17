#include <tgmath.h>

/* The test strategy here is just to attempt to call all of the
   type-generics with argument(s) of type 'long double' and, for those
   that can take a complex argument, also 'complex long double'.  This
   will provoke an error if one of the generics is missing or
   misimplemented.  Using 'double' or 'float' cannot be expected to do
   so, since the generics' names match <math.h>'s names with 'double'
   parameters, so argument promotion would make them appear to work
   even if the generic was absent.

   N.B. We don't attempt to validate the requirement to include <math.h>
   and <complex.h>.  */

void fr(long double xx, long double yy, long double zz)
{
  int ff;
  long double
    a = acos(xx),
    b = asin(xx),
    c = atan(xx),
    d = acosh(xx),
    e = asinh(xx),
    f = atanh(xx),
    g = cos(xx),
    h = sin(xx),
    i = tan(xx),
    j = cosh(xx),
    k = sinh(xx),
    l = tanh(xx),
    m = exp(xx),
    n = log(xx),
    o = pow(xx, yy),
    p = sqrt(xx),
    q = fabs(xx),

    r = atan2(xx, yy),
    s = cbrt(xx),
    t = ceil(xx),
    u = copysign(xx, yy),
    v = erf(xx),
    w = erfc(xx),
    x = exp2(xx),
    y = expm1(xx),
    z = fdim(xx, yy),
    aa= floor(xx),
    bb= fma(xx, yy, zz),
    cc= fmax(xx, yy),
    dd= fmin(xx, yy),
    ee= fmod(xx, yy),
    gg= frexp(xx, &ff),
    hh= hypot(xx, yy),
    ii= ldexp(xx, ff),
    jj= lgamma(xx),
    kk= log10(xx),
    ll= log1p(xx),
    mm= log2(xx),
    nn= logb(xx),
    oo= nearbyint(xx),
    pp= nextafter(xx, yy),
    qq= nexttoward(xx, yy),
    rr= remainder(xx, yy),
    ss= remquo(xx, yy, &ff),
    tt= rint(xx),
    uu= round(xx),
    vv= scalbn(xx, 22),
    ww= scalbln(xx, 22L),
   aaa= tgamma(xx),
   bbb= trunc(xx);

  int ccc = ilogb(xx);
  long
    ddd = lrint(xx),
    eee = lround(xx);
  long long
    fff = llrint(xx),
    ggg = llround(xx);
}

void fc(complex long double xx, complex long double yy)
{
  complex long double
    a = acos(xx),
    b = asin(xx),
    c = atan(xx),
    d = acosh(xx),
    e = asinh(xx),
    f = atanh(xx),
    g = cos(xx),
    h = sin(xx),
    i = tan(xx),
    j = cosh(xx),
    k = sinh(xx),
    l = tanh(xx),
    m = exp(xx),
    n = log(xx),
    o = pow(xx, yy),
    p = sqrt(xx),
    q = fabs(xx),

    r = carg(xx),
    s = cimag(xx),
    t = conj(xx),
    u = cproj(xx),
    v = creal(xx);
}
