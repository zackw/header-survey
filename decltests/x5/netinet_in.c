#include <netinet/in.h>

void f(void)
{
  in_port_t a;
  in_addr_t b;
  sa_family_t c;
  struct in_addr ia;
  in_addr_t *iaa = &ia.s_addr;
  struct sockaddr_in si;
  sa_family_t    *sif = &si.sin_family;
  in_port_t      *sip = &si.sin_port;
  struct in_addr *sia = &si.sin_addr;
/* sin_zero might be char[N] or unsigned char[N].  Since the only
   thing one should ever do to it is clear it, we just verify that
   it is, in fact, an array whose elements can be set to zero.
   (I would write memset(si.si_zero, 0, sizeof si.si_zero) but then
   I'd have to include string.h.) */
  si.sin_zero[0] = 0;

  int
    pa = IPPROTO_IP,
    pb = IPPROTO_ICMP,
    pc = IPPROTO_TCP,
    pd = IPPROTO_UDP;

  in_addr_t
    iany = INADDR_ANY,
    ibro = INADDR_BROADCAST;

  in_port_t an = htons((in_port_t)99);
  in_port_t ah = ntohs((in_port_t)99);
  in_addr_t bn = htonl(iany);
  in_addr_t bh = ntohl(iany);
}
