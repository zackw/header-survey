/* IPv6 support */
#include <netinet/in.h>

int xx[] = {
  IPPROTO_IPV6,
  IPV6_JOIN_GROUP,
  IPV6_LEAVE_GROUP,
  IPV6_MULTICAST_HOPS,
  IPV6_MULTICAST_IF,
  IPV6_MULTICAST_LOOP,
  IPV6_UNICAST_HOPS,
  IPV6_V6ONLY,
};

const struct in6_addr ANY = IN6ADDR_ANY_INIT;
const struct in6_addr LOOPBACK = IN6ADDR_LOOPBACK_INIT;

void f(void)
{
  char bb[INET6_ADDRSTRLEN];

  struct in6_addr
    cc = in6addr_any,
    dd = in6addr_loopback;

  struct ipv6_mreq ee;
  struct in6_addr *eea = &ee.ipv6mr_multiaddr;
  unsigned        *eeb = &ee.ipv6mr_interface;

  struct sockaddr_in6 ff;
  sa_family_t     *ffa = &ff.sin6_family;
  in_port_t       *ffb = &ff.sin6_port;
  uint32_t        *ffc = &ff.sin6_flowinfo;
  struct in6_addr *ffd = &ff.sin6_addr;
  uint32_t        *ffe = &ff.sin6_scope_id;

  struct in6_addr gg;
  uint8_t (*gga)[16] = &gg.s6_addr;
}
