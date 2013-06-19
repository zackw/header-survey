/* features */
#include <sys/socket.h>

int cc[] = {
  SOMAXCONN,
};

void f(void)
{
  struct sockaddr_storage ss;
  sa_family_t *ssf = &ss.ss_family;

  int (*a)(int) = sockatmark;
}
