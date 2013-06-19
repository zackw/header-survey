/* XSI features */
#include <sys/stat.h>
void f(void)
{
  int (*a)(int, const char *, mode_t, dev_t) = mknodat;
}
