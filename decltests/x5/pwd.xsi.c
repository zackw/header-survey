/* <code>getpwent</code>, <code>setpwent</code>, <code>endpwent</code> (XSI) */
#include <pwd.h>

void f(void)
{
  struct passwd *c = getpwent();

  setpwent();
  endpwent();
}
