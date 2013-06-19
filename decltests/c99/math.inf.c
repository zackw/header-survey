/* optional: <code>INFINITY</code> and <code>NAN</code> */
#include <math.h>

void tm(void)
{
  /* INFINITY is mandatory, but if infinities are not supported, it
     will expand to "a positive constant of type `float` that
     overflows at translation time" ...in which case using it is a
     constraint violation, according to footnote 192.  Feh.  */
  float ii = INFINITY;

  /* "The macro `NAN` is defined if and only if the implementation
     supports quiet NaNs for the `float` type." */
  float nn = NAN;
}
