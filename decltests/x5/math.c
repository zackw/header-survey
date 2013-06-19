/* XSI: features */
#include <math.h>

/* gamma silently removed in Issue 6; scalb silently removed in Issue 7 */
/* MAXFLOAT marked obsolete in Issue 7 */

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
  int *o = &signgam;

  /* note: functions incorporated into C99 are not listed here */
  /* note: gamma, scalb removed in X7 */
  double
    p = j0(a),
    q = j1(a),
    r = jn(a, 2),
    s = y0(a),
    t = y1(a),
    u = yn(a, 2);
}
