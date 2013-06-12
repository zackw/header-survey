/* baseline */
#include <signal.h>

static volatile sig_atomic_t v;

static void handler(int x)
{
  v = (sig_atomic_t)x;
}

void f(void)
{
  int a = signal(SIGABRT, SIG_DFL) != SIG_ERR;
  int b = signal(SIGFPE,  SIG_DFL) != SIG_ERR;
  int c = signal(SIGILL,  SIG_IGN) != SIG_ERR;
  int d = signal(SIGINT,  SIG_IGN) != SIG_ERR;
  int e = signal(SIGSEGV, handler) != SIG_ERR;
  int f = signal(SIGTERM, handler) != SIG_ERR;

  int g = raise(SIGTERM);
}
