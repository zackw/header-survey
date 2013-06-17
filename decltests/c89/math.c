#include <math.h>

void f(double x, double y)
{
  double huge = HUGE_VAL;

  double a = acos(x);
  double b = asin(x);
  double c = atan(x);
  double d = atan2(x, y);

  double e = cos(x);
  double f = sin(x);
  double g = tan(x);

  double h = cosh(x);
  double i = sinh(x);
  double j = tanh(x);

  double k = exp(x);
  double l = log(x);
  double m = log10(x);
  double n = pow(x, y);
  double o = sqrt(x);

  int ee;
  double ii;
  double p = frexp(x, &ee);
  double q = ldexp(y, ee);
  double r = modf(x, &ii);

  double s = ceil(x);
  double t = fabs(x);
  double u = floor(x);
  double v = fmod(x, y);
}
