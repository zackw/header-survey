#include <net/if.h>

void f(void)
{
  struct if_nameindex aa;
  unsigned *aai = &aa.if_index;
  char    **aan = &aa.if_name;

  char bb[IF_NAMESIZE];

  unsigned              (*ca)(const char *) = if_nametoindex;
  char                 *(*cb)(unsigned, char *) = if_indextoname;
  struct if_nameindex  *(*cc)(void) = if_nameindex;
  void                  (*cd)(struct if_nameindex *) = if_freenameindex;
}
