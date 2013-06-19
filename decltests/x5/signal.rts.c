/* optional: realtime signals */
#include <signal.h>

int xx[] = {
  SIGEV_NONE,
  SIGEV_SIGNAL,
  SIGEV_THREAD,

  SI_QUEUE,
};

void t(void)
{
  /* these are not necessarily compile-time constants */
  int xa = SIGRTMIN;
  int xb = SIGRTMAX;

  struct sigevent se;
  int *sen = &se.sigev_notify;
  int *ses = &se.sigev_signo;
  void (**senf)(union sigval) = &se.sigev_notify_function;
  pthread_attr_t **sena = &se.sigev_notify_attributes;

  union sigval *sev = &se.sigev_value;
  int *sevi = &sev->sival_int;
  void **sevp = &sev->sival_ptr;

  siginfo_t si;
  union sigval *siv = &si.si_value;
}

void f(void)
{
  int (*a)(pid_t, int, const union sigval) = sigqueue;
  int (*b)(const sigset_t *, siginfo_t *, const struct timespec *)
    = sigtimedwait;
  int (*c)(const sigset_t *, siginfo_t *) = sigwaitinfo;
}
