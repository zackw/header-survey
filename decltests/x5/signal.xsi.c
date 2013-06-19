/* XSI signal extensions */
#include <signal.h>

/* sighold, sigignore, siginterrupt, sigpause, sigrelse, sigset
   obsolescent in Issue 7

   bsd_signal obsolescent in Issue 6, removed in 7

   sigstack obsolescent in Issue 5, removed in 6
   (struct sigstack "should have been removed" at the same time,
   but wasn't actually till 7).

   SIGPOLL, SIGPROF, and si_band are marked as obsolescent (STREAMS)
   in Issue 7, but I'm leaving them in unless/until I find a system
   that actually removed them.  */

int xx[] = {
  SIGPOLL,
  SIGPROF,
  SIGSYS,
  SIGTRAP,
  SIGVTALRM,
  SIGXCPU,
  SIGXFSZ,

  SA_ONSTACK,
  SA_RESETHAND,
  SA_RESTART,
  SA_SIGINFO,
  SA_NOCLDWAIT,
  SA_NODEFER,

  SS_DISABLE,
  SS_ONSTACK,
  MINSIGSTKSZ,
  SIGSTKSZ,

  ILL_ILLOPC,
  ILL_ILLOPN,
  ILL_ILLADR,
  ILL_ILLTRP,
  ILL_PRVOPC,
  ILL_PRVREG,
  ILL_COPROC,
  ILL_BADSTK,

  FPE_INTDIV,
  FPE_INTOVF,
  FPE_FLTDIV,
  FPE_FLTOVF,
  FPE_FLTUND,
  FPE_FLTRES,
  FPE_FLTINV,
  FPE_FLTSUB,

  SEGV_MAPERR,
  SEGV_ACCERR,

  BUS_ADRALN,
  BUS_ADRERR,
  BUS_OBJERR,

  TRAP_BRKPT,
  TRAP_TRACE,

  CLD_EXITED,
  CLD_KILLED,
  CLD_DUMPED,
  CLD_TRAPPED,
  CLD_STOPPED,
  CLD_CONTINUED,

  POLL_IN,
  POLL_OUT,
  POLL_MSG,
  POLL_ERR,
  POLL_PRI,
  POLL_HUP,
};

void t(void)
{
  stack_t ss;
  void **ssp = &ss.ss_sp;
  size_t *sss = &ss.ss_size;
  int *ssf = &ss.ss_flags;

  siginfo_t si;
  int   *sie = &si.si_errno;
  pid_t *sip = &si.si_pid;
  uid_t *siu = &si.si_uid;
  void **sia = &si.si_addr;
  int   *sit = &si.si_status;
  long  *sib = &si.si_band;
}

void f(void)
{
  int (*a)(pid_t, int) = killpg;
  int (*b)(const stack_t *, stack_t *) = sigaltstack;
}
