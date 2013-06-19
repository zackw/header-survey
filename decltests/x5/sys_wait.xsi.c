/* XSI: features */
#include <sys/wait.h>

void wmacros(int ss)
{
  int
    a = WIFCONTINUED(ss),
    b = WEXITED,
    c = WSTOPPED,
    d = WCONTINUED,
    g = WNOWAIT;

  idtype_t
    m = P_ALL,
    n = P_PID,
    o = P_PGID;
}

void f(void)
{
  int (*a)(idtype_t, id_t, siginfo_t *, int) = waitid;
}
