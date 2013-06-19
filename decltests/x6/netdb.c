/* the <code>getaddrinfo</code> family */
#include <netdb.h>

int xx[] = {
  AI_PASSIVE,
  AI_CANONNAME,
  AI_NUMERICHOST,
  AI_NUMERICSERV,
  AI_V4MAPPED,
  AI_ALL,
  AI_ADDRCONFIG,

  NI_NOFQDN,
  NI_NUMERICHOST,
  NI_NAMEREQD,
  NI_NUMERICSERV,
  NI_DGRAM,

  EAI_AGAIN,
  EAI_BADFLAGS,
  EAI_FAIL,
  EAI_FAMILY,
  EAI_MEMORY,
  EAI_NONAME,
  EAI_SERVICE,
  EAI_SOCKTYPE,
  EAI_SYSTEM,
  EAI_OVERFLOW,
};

void f(void)
{
  struct addrinfo ai;
  int              *aifl = &ai.ai_flags;
  int              *aifa = &ai.ai_family;
  int              *aiso = &ai.ai_socktype;
  int              *aipr = &ai.ai_protocol;
  socklen_t        *aial = &ai.ai_addrlen;
  struct sockaddr **aiad = &ai.ai_addr;
  char            **aica = &ai.ai_canonname;
  struct addrinfo **aine = &ai.ai_next;

  void        (*aa)(struct addrinfo *) = freeaddrinfo;
  const char *(*ab)(int) = gai_strerror;
  int         (*ac)(const char *, const char *,
                    const struct addrinfo *,
                    struct addrinfo **) = getaddrinfo;
  int         (*ad)(const struct sockaddr *, socklen_t,
                    char *, socklen_t, char *, socklen_t, int) = getnameinfo;
}
