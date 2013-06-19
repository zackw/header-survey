/* IPv6 address classification macros */
#include <netinet/in.h>

/* Some versions of glibc are a little bit too clever about these,
   causing them not to work with gcc in strict conformance mode with
   optimization on.  */

void f(struct in6_addr *aa)
{
  int
    a = IN6_IS_ADDR_UNSPECIFIED(aa),
    b = IN6_IS_ADDR_LOOPBACK(aa),
    c = IN6_IS_ADDR_MULTICAST(aa),
    d = IN6_IS_ADDR_LINKLOCAL(aa),
    e = IN6_IS_ADDR_SITELOCAL(aa),
    f = IN6_IS_ADDR_V4MAPPED(aa),
    g = IN6_IS_ADDR_V4COMPAT(aa),
    h = IN6_IS_ADDR_MC_NODELOCAL(aa),
    i = IN6_IS_ADDR_MC_LINKLOCAL(aa),
    j = IN6_IS_ADDR_MC_SITELOCAL(aa),
    k = IN6_IS_ADDR_MC_ORGLOCAL(aa),
    l = IN6_IS_ADDR_MC_GLOBAL(aa);
}
