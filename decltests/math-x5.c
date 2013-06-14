/* SUSv2 additions */
#include <math.h>

void f(void)
{
  double
    a = M_E,
    b = M_LOG2E,
    c = M_LOG10E,
    d = M_LN2,
    e = M_LN10,
    f = M_PI,
    g = M_PI_2,
    h = M_PI_4,
    i = M_1_PI,
    j = M_2_PI,
    k = M_2_SQRTPI,
    l = M_SQRT2,
    m = M_SQRT1_2;
  float n = MAXFLOAT;
  int *o = &signgam;

  /* note: functions incorporated into C99 are not listed here */
  double
    p = gamma(a),
    q = j0(a),
    r = j1(a),
    s = jn(a, 2),
    t = y0(a),
    u = y1(a),
    v = yn(a, 2),
    w = scalb(a, b);
}
