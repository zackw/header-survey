/* <code>psignal</code> and <code>psiginfo</code> */
#include <signal.h>

void f(void)
{
  void (*a)(const siginfo_t *, const char *) = psiginfo;
  void (*b)(int, const char *) = psignal;
}
