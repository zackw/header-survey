/* additional POSIX and XSI constants and functions */
#include <signal.h>

void k(void)
{
  void (*aa)(int) = SIG_HOLD;

  int
    ab = SIGEV_NONE,
    ac = SIGEV_SIGNAL,
    ad = SIGEV_THREAD,
    ae = SIGRTMIN,
    af = SIGRTMAX,

    ag = SIGALRM,
    ah = SIGHUP,
    ai = SIGKILL,
    aj = SIGPIPE,
    ak = SIGQUIT,
    al = SIGUSR1,
    am = SIGUSR2,
    an = SIGCHLD,
    ao = SIGCONT,
    ap = SIGSTOP,
    aq = SIGTSTP,
    ar = SIGTTIN,
    as = SIGTTOU,
    at = SIGBUS,
    au = SIGPOLL,
    av = SIGPROF,
    aw = SIGSYS,
    ax = SIGTRAP,
    ay = SIGURG,
    az = SIGVTALRM,
    ba = SIGXCPU,
    bb = SIGXFSZ,

    bc = SIG_BLOCK,
    bd = SIG_SETMASK,
    be = SIG_UNBLOCK,

    bf = SA_NOCLDSTOP,
    bg = SA_NOCLDWAIT,
    bh = SA_NODEFER,
    bi = SA_ONSTACK,
    bj = SA_RESETHAND,
    bk = SA_RESTART,
    bl = SA_SIGINFO,

    bm = SS_DISABLE,
    bn = SS_ONSTACK,
    bo = MINSIGSTKSZ,
    bp = SIGSTKSZ,

    bq = ILL_ILLOPC,
    br = ILL_ILLOPN,
    bs = ILL_ILLADR,
    bt = ILL_ILLTRP,
    bu = ILL_PRVOPC,
    bv = ILL_PRVREG,
    bw = ILL_COPROC,
    bx = ILL_BADSTK,

    by = FPE_INTDIV,
    bz = FPE_INTOVF,
    ca = FPE_FLTDIV,
    cb = FPE_FLTOVF,
    cc = FPE_FLTUND,
    cd = FPE_FLTRES,
    ce = FPE_FLTINV,
    cf = FPE_FLTSUB,

    cg = SEGV_MAPERR,
    ch = SEGV_ACCERR,

    ci = BUS_ADRALN,
    cj = BUS_ADRERR,
    ck = BUS_OBJERR,

    cl = TRAP_BRKPT,
    cm = TRAP_TRACE,

    cn = CLD_EXITED,
    co = CLD_KILLED,
    cp = CLD_DUMPED,
    cq = CLD_TRAPPED,
    cr = CLD_STOPPED,
    cs = CLD_CONTINUED,

    ct = POLL_IN,
    cu = POLL_OUT,
    cv = POLL_MSG,
    cw = POLL_ERR,
    cx = POLL_PRI,
    cy = POLL_HUP,

    cz = SI_USER,
    da = SI_QUEUE,
    db = SI_TIMER,
    dc = SI_ASYNCIO,
    dd = SI_MESGQ;
}

void t(void)
{
  struct sigevent se;
  int *sen = &se.sigev_notify;
  int *ses = &se.sigev_signo;
  void (**senf)(union sigval) = &se.sigev_notify_function;
  pthread_attr_t **sena = &se.sigev_notify_attributes;

  union sigval *sev = &se.sigev_value;
  int *sevi = &sev->sival_int;
  void **sevp = &sev->sival_ptr;

  struct sigaction sa;
  void (**sah)(int) = &sa.sa_handler;
  void (**saa)(int, siginfo_t *, void *) = &sa.sa_sigaction;
  sigset_t *sam = &sa.sa_mask;
  int *saf = &sa.sa_flags;

  stack_t ss;
  void **ssp = &ss.ss_sp;
  size_t *sss = &ss.ss_size;
  int *ssf = &ss.ss_flags;

  struct sigstack st;
  int *sto = &st.ss_onstack;
  void **stp = &st.ss_sp;

  siginfo_t si;
  int   *sis = &si.si_signo;
  int   *sie = &si.si_errno;
  int   *sic = &si.si_code;
  pid_t *sip = &si.si_pid;
  uid_t *siu = &si.si_uid;
  void **sia = &si.si_addr;
  int   *sit = &si.si_status;
  long  *sib = &si.si_band;
  union sigval *siv = &si.si_value;

  ucontext_t uc; /* validated elsewhere */
}

typedef void (*handler)(int);

void f(pid_t aa, int bb, pthread_t cc,
       const sigset_t *dd, sigset_t *ee,
       const struct sigaction *ff, struct sigaction *gg,
       const stack_t *hh, stack_t *ii,
       const union sigval jj,
       siginfo_t *kk,
       const struct timespec *ll,
       handler mm)
{
  int
    a = kill(aa, bb),
    b = killpg(aa, bb),
    c = pthread_kill(cc, bb),
    d = pthread_sigmask(bb, dd, ee),
    f = sigaction(bb, ff, gg),
    g = sigaddset(ee, bb),
    h = sigaltstack(hh, ii),
    i = sigdelset(ee, bb),
    j = sigemptyset(ee),
    k = sigfillset(ee),
    l = sighold(bb),
    m = sigignore(bb),
    n = siginterrupt(bb, 1),
    o = sigismember(ee, bb),
    p = sigpause(bb),
    q = sigpending(ee),
    r = sigprocmask(bb, dd, ee),
    s = sigqueue(aa, bb, jj),
    t = sigrelse(bb),
    u = sigsuspend(dd),
    v = sigtimedwait(dd, kk, ll),
    w = sigwait(dd, &bb),
    x = sigwaitinfo(dd, kk);

  handler y = sigset(bb, mm);

  /* bsd_signal and sigstack are obsolete, so not tested */
}
