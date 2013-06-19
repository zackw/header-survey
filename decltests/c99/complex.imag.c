/* optional: imaginary types */
#include <complex.h>

/* This #ifndef is not strictly necessary but
   cuts down on logfile chatter. */
#ifndef imaginary
#error "imaginary types explicitly unsupported"
#else
void ti(void)
{
  imaginary float        a = 1.0f*I;
  imaginary double       b = 2.0 *I;
  imaginary long double  c = 4.0l*I;

  _Imaginary float       d = 1.0f * _Imaginary_I;
  _Imaginary double      e = 2.0  * _Imaginary_I;
  _Imaginary long double f = 4.0l * _Imaginary_I;
}
#endif
