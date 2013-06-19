/* scheduling priority and scope */
#include <pthread.h>

int xx[] = {
  PTHREAD_PRIO_INHERIT,
  PTHREAD_PRIO_NONE,
  PTHREAD_PRIO_PROTECT,
  PTHREAD_SCOPE_PROCESS,
  PTHREAD_SCOPE_SYSTEM,
};

void f(void)
{
  int (*a)(const pthread_attr_t *, int *) = pthread_attr_getinheritsched;
  int (*b)(const pthread_attr_t *, int *) = pthread_attr_getschedpolicy;
  int (*c)(const pthread_attr_t *, int *) = pthread_attr_getscope;
  int (*d)(pthread_attr_t *, int) = pthread_attr_setinheritsched;
  int (*e)(pthread_attr_t *, int) = pthread_attr_setschedpolicy;
  int (*f)(pthread_attr_t *, int) = pthread_attr_setscope;
  int (*g)(pthread_t, int *, struct sched_param *) = pthread_getschedparam;
  int (*h)(pthread_t, int, const struct sched_param *) = pthread_setschedparam;
  int (*i)(const pthread_mutex_t *, int *) = pthread_mutex_getprioceiling;
  int (*j)(pthread_mutex_t *, int, int *) = pthread_mutex_setprioceiling;
  int (*k)(const pthread_mutexattr_t *, int *)
    = pthread_mutexattr_getprioceiling;
  int (*l)(const pthread_mutexattr_t *, int *)
    = pthread_mutexattr_getprotocol;
  int (*m)(pthread_mutexattr_t *, int) = pthread_mutexattr_setprioceiling;
  int (*n)(pthread_mutexattr_t *, int) = pthread_mutexattr_setprotocol;
}
