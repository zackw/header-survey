#include <sys/resource.h>

int cc[] = {
  PRIO_PROCESS,
  PRIO_PGRP,
  PRIO_USER,

  RUSAGE_SELF,
  RUSAGE_CHILDREN,

  RLIMIT_CORE,
  RLIMIT_CPU,
  RLIMIT_DATA,
  RLIMIT_FSIZE,
  RLIMIT_NOFILE,
  RLIMIT_STACK,
  RLIMIT_AS
};

rlim_t cr[] = {
  RLIM_INFINITY,
  RLIM_SAVED_MAX,
  RLIM_SAVED_CUR,
};

void f(id_t aa)
{
  struct rlimit rl;
  rlim_t *rlc = &rl.rlim_cur;
  rlim_t *rlm = &rl.rlim_max;

  struct rusage ru;
  struct timeval *ruu = &ru.ru_utime;
  struct timeval *rus = &ru.ru_stime;

  int a = getpriority(PRIO_PROCESS, aa);
  int b = setpriority(PRIO_PROCESS, aa, a - 5);

  int c = getrlimit(RLIMIT_CPU, &rl);
  int d = setrlimit(RLIMIT_STACK, &rl);

  int e = getrusage(RUSAGE_SELF, &ru);
}
