#include <netinet/tcp.h>

/* Yes, this really is the only thing, of all the dozens of things in
   netinet/tcp.h, that's standardized.  Even in Issue 7.  */
int xx[] = {
  TCP_NODELAY,
};
