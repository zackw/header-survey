#include <sys/wait.h>

void wmacros(int ss)
{
  int
    a = WEXITSTATUS(ss),
    b = WIFEXITED(ss),
    c = WIFSIGNALED(ss),
    d = WIFSTOPPED(ss),
    e = WSTOPSIG(ss),
    f = WTERMSIG(ss),
    g = WCONTINUED,
    h = WEXITED,
    i = WSTOPPED,
    j = WUNTRACED,
    k = WNOHANG,
    l = WNOWAIT;

  idtype_t
    m = P_ALL,
    n = P_PID,
    o = P_PGID;
}

void f(idtype_t aa, id_t bb, pid_t cc, struct rusage *dd, siginfo_t *ee)
{
  int a;
  pid_t b = wait(&a);
  pid_t c = wait3(&a, WNOHANG, dd);
  int   d = waitid(aa, bb, ee, WNOWAIT);
  pid_t e = waitpid(cc, &a, WEXITED|WCONTINUED);
}
