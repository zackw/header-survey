/* <code>utimes</code> */
#include <sys/time.h>

/* marked LEGACY in issue 6, silently reverted in 7 */

void f(void)
{
  struct timeval tf[2];
  int f = utimes("thingy", tf);
}
