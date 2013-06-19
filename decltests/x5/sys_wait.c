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
    g = WNOHANG,
    h = WUNTRACED;
}

/* wait3 removed in Issue 6 */

void f(void)
{
  pid_t (*a)(int *) = wait;
  pid_t (*b)(pid_t, int *, int) = waitpid;
}
