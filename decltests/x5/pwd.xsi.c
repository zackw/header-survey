/* XSI: <code>getpwent</code>, <code>setpwent</code>, <code>endpwent</code> */
#include <pwd.h>

void f(void)
{
  struct passwd *c = getpwent();

  setpwent();
  endpwent();
}
