#include <complex.h>

void tc(void)
{
  complex float        a = 1.0f + 1.0f*I;
  complex double       b = 2.0  + 2.0 *I;
  complex long double  c = 4.0l + 4.0l*I;

  _Complex float       d = 1.0f + 1.0f * _Complex_I;
  _Complex double      e = 2.0  + 2.0  * _Complex_I;
  _Complex long double f = 4.0l + 4.0l * _Complex_I;
}

void ff(complex float zz, complex float ww)
{
  complex float
    a = cacosf(zz),
    b = casinf(zz),
    c = catanf(zz),
    d = ccosf(zz),
    e = csinf(zz),
    f = ctanf(zz),
    g = cacoshf(zz),
    h = casinhf(zz),
    i = catanhf(zz),
    j = ccoshf(zz),
    k = csinhf(zz),
    l = ctanhf(zz),
    m = cexpf(zz),
    n = clogf(zz),
    p = cpowf(zz, ww),
    q = csqrtf(zz),
    t = conjf(zz),
    u = cprojf(zz);

  float
    o = cabsf(zz),
    r = cargf(zz),
    s = cimagf(zz),
    v = crealf(zz);
}

void fd(complex double zz, complex double ww)
{
  complex double
    a = cacos(zz),
    b = casin(zz),
    c = catan(zz),
    d = ccos(zz),
    e = csin(zz),
    f = ctan(zz),
    g = cacosh(zz),
    h = casinh(zz),
    i = catanh(zz),
    j = ccosh(zz),
    k = csinh(zz),
    l = ctanh(zz),
    m = cexp(zz),
    n = clog(zz),
    p = cpow(zz, ww),
    q = csqrt(zz),
    t = conj(zz),
    u = cproj(zz);

  double
    o = cabs(zz),
    r = carg(zz),
    s = cimag(zz),
    v = creal(zz);
}

void fl(complex long double zz, complex long double ww)
{
  complex long double
    a = cacosl(zz),
    b = casinl(zz),
    c = catanl(zz),
    d = ccosl(zz),
    e = csinl(zz),
    f = ctanl(zz),
    g = cacoshl(zz),
    h = casinhl(zz),
    i = catanhl(zz),
    j = ccoshl(zz),
    k = csinhl(zz),
    l = ctanhl(zz),
    m = cexpl(zz),
    n = clogl(zz),
    p = cpowl(zz, ww),
    q = csqrtl(zz),
    t = conjl(zz),
    u = cprojl(zz);

  long double
    o = cabsl(zz),
    r = cargl(zz),
    s = cimagl(zz),
    v = creall(zz);
}
