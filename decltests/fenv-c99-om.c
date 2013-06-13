/* C99: optional macros */
#include <fenv.h>
#pragma STDC FENV_ACCESS ON

void m(void)
{
  int a = fetestexcept(FE_DIVBYZERO|
                       FE_INEXACT|
                       FE_INVALID|
                       FE_OVERFLOW|
                       FE_UNDERFLOW);
  int b = fegetround();
  int c = (b == FE_DOWNWARD);
  int d = (b == FE_TONEAREST);
  int e = (b == FE_TOWARDZERO);
  int f = (b == FE_UPWARD);
}
