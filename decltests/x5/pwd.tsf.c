/* <code>getpwnam_r</code> and <code>getpwuid_r</code> */
#include <pwd.h>

void f(const char *bb, uid_t cc)
{
  struct passwd aa;
  struct passwd *dd;
  char ee[512];
  int d = getpwnam_r(bb, &aa, ee, sizeof ee, &dd);
  int e = getpwuid_r(cc, &aa, ee, sizeof ee, &dd);
}
