/* baseline */
#include <sys/utsname.h>

void f(void)
{
  struct utsname a;
  int b = uname(&a);
  char *c = a.sysname;
  char *d = a.nodename;
  char *e = a.release;
  char *f = a.version;
  char *g = a.machine;
}
