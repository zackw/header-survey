/* baseline */
#include <fenv.h>
#pragma STDC FENV_ACCESS ON

void f(void)
{
  fexcept_t fexc;
  fenv_t fenv;
  int a, b, c, d;

  fegetexceptflag(&fexc, FE_ALL_EXCEPT);
  feclearexcept(FE_ALL_EXCEPT);
  feraiseexcept(FE_ALL_EXCEPT);
  fesetexceptflag(&fexc, FE_ALL_EXCEPT);
  a = fetestexcept(FE_ALL_EXCEPT);

  b = fegetround();
  c = fesetround(0); /* no rounding direction macros are guaranteed */

  fegetenv(&fenv);
  d = feholdexcept(&fenv);
  fesetenv(FE_DFL_ENV);
  feupdateenv(&fenv);
}
