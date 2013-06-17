#include <sys/un.h>

void f(void)
{
  struct sockaddr_un sun;
  sa_family_t *f = &sun.sun_family;
  char *p = sun.sun_path;
}
