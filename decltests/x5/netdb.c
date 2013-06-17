#include <netdb.h>

void f(const char *name,
       const void *addr, size_t len, int type,
       uint32_t net,
       int port,
       int proto,
       const char *protoname)
{
  struct hostent ah;
  char  **ahnm = &ah.h_name;
  char ***aha  = &ah.h_aliases;
  int    *ahad = &ah.h_addrtype;
  int    *ahl  = &ah.h_length;
  char ***ahal = &ah.h_addr_list;

  struct netent an;
  char  **annm = &an.n_name;
  char ***ana  = &an.n_aliases;
  int    *anad = &an.n_addrtype;
  uint32_t *ann= &an.n_net;

  struct protoent ap;
  char  **apnm = &ap.p_name;
  char ***apa  = &ap.p_aliases;
  int    *app  = &ap.p_proto;

  struct servent as;
  char  **asnm = &as.s_name;
  char ***asa  = &as.s_aliases;
  int    *asp  = &as.s_port;
  char  **aspr = &as.s_proto;

  int *ae = &h_errno;

  int
    ir = IPPORT_RESERVED,
    ea = HOST_NOT_FOUND,
    eb = NO_DATA,
    ec = NO_RECOVERY,
    ef = TRY_AGAIN;

  struct hostent *h;
  struct netent *n;
  struct protoent *p;
  struct servent *s;

  sethostent(1);
  setnetent(1);
  setprotoent(1);
  setservent(1);

  h = gethostbyaddr(addr, len, type);
  h = gethostbyname(name);
  h = gethostent();

  n = getnetbyaddr(net, type);
  n = getnetbyname(name);
  n = getnetent();

  p = getprotobyname(protoname);
  p = getprotobynumber(proto);
  p = getprotoent();

  s = getservbyname(name, protoname);
  s = getservbyport(port, protoname);
  s = getservent();

  endhostent();
  endnetent();
  endprotoent();
  endservent();
}
