#include <sys/socket.h>

int cc[] = {
  SCM_RIGHTS,

  SOCK_DGRAM,
  SOCK_STREAM,
  SOCK_SEQPACKET,

  SOL_SOCKET,

  SO_ACCEPTCONN,
  SO_BROADCAST,
  SO_DEBUG,
  SO_DONTROUTE,
  SO_ERROR,
  SO_KEEPALIVE,
  SO_LINGER,
  SO_OOBINLINE,
  SO_RCVBUF,
  SO_RCVLOWAT,
  SO_RCVTIMEO,
  SO_REUSEADDR,
  SO_SNDBUF,
  SO_SNDLOWAT,
  SO_SNDTIMEO,
  SO_TYPE,

  MSG_CTRUNC,
  MSG_DONTROUTE,
  MSG_EOR,
  MSG_OOB,
  MSG_PEEK,
  MSG_TRUNC,
  MSG_WAITALL,

  AF_UNIX,
  AF_UNSPEC,
  AF_INET,

  SHUT_RD,
  SHUT_WR,
  SHUT_RDWR,
};

void ff(struct msghdr *sm)
{
  struct sockaddr sa;
  sa_family_t *saf = &sa.sa_family;
  char        *sad =  sa.sa_data;

  struct linger sl;
  int *slo = &sl.l_onoff;
  int *sll = &sl.l_linger;

  void         **smn  = &sm->msg_name;
  socklen_t     *smnl = &sm->msg_namelen;
  struct iovec **smi  = &sm->msg_iov;
  size_t         smil =  sm->msg_iovlen;  /* see sys_socket.mht.c */
  void         **smc  = &sm->msg_control;
  size_t         smcl =  sm->msg_controllen; /* ditto */
  int           *smf  = &sm->msg_flags;

  struct cmsghdr *sc  = CMSG_FIRSTHDR(sm);
  size_t          scl =  sc->cmsg_len;       /* ditto */
  int            *scv = &sc->cmsg_level;
  int            *sct = &sc->cmsg_type;
  unsigned char  *scd = CMSG_DATA(sc);
  struct cmsghdr *scn = CMSG_NXTHDR(sm, sc);

  int     (*a)(int, struct sockaddr *, socklen_t *) = accept;
  int     (*b)(int, const struct sockaddr *, socklen_t) = bind;
  int     (*c)(int, const struct sockaddr *, socklen_t) = connect;
  int     (*d)(int, struct sockaddr *, socklen_t *) = getpeername;
  int     (*e)(int, struct sockaddr *, socklen_t *) = getsockname;
  int     (*f)(int, int, int, void *, socklen_t *) = getsockopt;
  int     (*g)(int, int) = listen;
  ssize_t (*h)(int, void *, size_t, int) = recv;
  ssize_t (*i)(int, void *, size_t, int, struct sockaddr *, socklen_t *)
    = recvfrom;
  ssize_t (*j)(int, struct msghdr *, int) = recvmsg;
  ssize_t (*k)(int, const void *, size_t, int) = send;
  ssize_t (*l)(int, const struct msghdr *, int) = sendmsg;
  ssize_t (*m)(int, const void *, size_t, int, const struct sockaddr *,
               socklen_t) = sendto;
  int     (*n)(int, int, int, const void *, socklen_t) = setsockopt;
  int     (*o)(int, int) = shutdown;
  int     (*p)(int, int, int) = socket;
  int     (*q)(int, int, int, int[2]) = socketpair;
}
