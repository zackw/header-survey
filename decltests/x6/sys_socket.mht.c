/* correct types for <code>msg_iovlen</code>, <code>msg_controllen</code>, and <code>cmsg_len</code> */
#include <sys/socket.h>

/* The structure fields msg_iovlen, msg_controllen, and cmsg_len are
   all supposed to be size_t quantities, but prior to Issue 6 some
   of them were socklen_t or int, and not everyone has caught up.
   So the base sys_socket.c only checks that the fields exist,
   whereas this file enforces fully correct declarations. */

void ff(struct msghdr *sm, struct cmsghdr *sc)
{
  size_t        *smil = &sm->msg_iovlen;
  size_t        *smcl = &sm->msg_controllen;
  size_t         *scl = &sc->cmsg_len;
}
