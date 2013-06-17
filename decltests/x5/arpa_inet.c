#include <arpa/inet.h>

void f(uint32_t aa, uint16_t bb, const char *cc,
       struct in_addr dd, in_addr_t ee, in_addr_t ff)
{
  uint32_t a = htonl(aa);
  uint32_t b = ntohl(aa);
  uint16_t c = htons(bb);
  uint16_t d = ntohs(bb);

  in_addr_t      e = inet_addr(cc);
  in_addr_t      f = inet_lnaof(dd);
  struct in_addr g = inet_makeaddr(ee, ff);
  in_addr_t      h = inet_netof(dd);
  in_addr_t      i = inet_network(cc);
  char          *j = inet_ntoa(dd);

  in_port_t      k;
}
