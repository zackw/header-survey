#include <arpa/inet.h>

/* inet_lnaof, inet_netof, inet_makeaddr, inet_network are in Issue 5
   but vanished from Issue 6 without explanation or even acknowledgment.
   The former three are obsolete due to CIDR, and it's not clear how the
   latter is different from inet_addr, so maybe that's why. */

void f(uint32_t aa, uint16_t bb, const char *cc,
       struct in_addr dd, in_addr_t ee, in_addr_t ff)
{
  uint32_t a = htonl(aa);
  uint32_t b = ntohl(aa);
  uint16_t c = htons(bb);
  uint16_t d = ntohs(bb);

  in_addr_t      e = inet_addr(cc);
  char          *f = inet_ntoa(dd);

  in_port_t      g;
}
