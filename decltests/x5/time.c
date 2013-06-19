/* features */
#include <time.h>

/* CLK_TCK skipped, legacy */

void f(void)
{
  void (*a)(void) = tzset;
  char **b = tzname;
}
