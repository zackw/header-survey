/* imaginary types (optional in C99) */
#include <complex.h>

void ti(void)
{
  imaginary float        a = 1.0f*I;
  imaginary double       b = 2.0 *I;
  imaginary long double  c = 4.0l*I;

  _Imaginary float       d = 1.0f * _Imaginary_I;
  _Imaginary double      e = 2.0  * _Imaginary_I;
  _Imaginary long double f = 4.0l * _Imaginary_I;
}
