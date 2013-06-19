/* features */
#include <signal.h>

int xx[] = {
  SIGALRM,
  SIGBUS,
  SIGCHLD,
  SIGCONT,
  SIGHUP,
  SIGKILL,
  SIGPIPE,
  SIGQUIT,
  SIGSTOP,
  SIGTSTP,
  SIGTTIN,
  SIGTTOU,
  SIGURG,
  SIGUSR1,
  SIGUSR2,

  SA_NOCLDSTOP,

  SIG_BLOCK,
  SIG_UNBLOCK,
  SIG_SETMASK,

  SI_USER,
  SI_TIMER,
  SI_ASYNCIO,
  SI_MESGQ,
};

void (*xy[])(int) = {
  SIG_HOLD,
};

void t(void)
{
 struct sigaction sa;
  void (**sah)(int) = &sa.sa_handler;
  void (**saa)(int, siginfo_t *, void *) = &sa.sa_sigaction;
  sigset_t *sam = &sa.sa_mask;
  int *saf = &sa.sa_flags;

  siginfo_t si;
  int   *sis = &si.si_signo;
  int   *sic = &si.si_code;

  sigset_t sg;   /* opaque */
  pid_t p;       /* integral */
}

typedef void (*handler)(int);

void f(void)
{
  int (*a)(pid_t, int) = kill;
  int (*b)(int, const struct sigaction *, struct sigaction *) = sigaction;
  int (*c)(sigset_t *, int) = sigaddset;
  int (*d)(sigset_t *, int) = sigdelset;
  int (*e)(sigset_t *) = sigemptyset;
  int (*f)(sigset_t *) = sigfillset;
  int (*g)(const sigset_t *, int) = sigismember;
  int (*h)(sigset_t *) = sigpending;
  int (*i)(int, const sigset_t *, sigset_t *) = sigprocmask;
  int (*j)(const sigset_t *) = sigsuspend;
  int (*k)(const sigset_t *, int *) = sigwait;
}
