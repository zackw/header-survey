/* <code>NI_NUMERICSCOPE</code> */
#include <netdb.h>

/* Despite having been in POSIX for as long as getnameinfo itself has,
   NI_NUMERICSCOPE was not in RFC 3493 and therefore seems to have been
   left out of prominent implementations that are otherwise fully compliant
   (e.g. glibc: http://sourceware.org/bugzilla/show_bug.cgi?id=14102 )
   We therefore split it from x6/netdb.c to avoid giving the impression
   that said implementations lack getnameinfo. */

int xx[] = {
  NI_NUMERICSCOPE,
};
