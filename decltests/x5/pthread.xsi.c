/* XSI features */
#include <pthread.h>

int xx[] = {
  PTHREAD_MUTEX_DEFAULT,
  PTHREAD_MUTEX_ERRORCHECK,
  PTHREAD_MUTEX_NORMAL,
  PTHREAD_MUTEX_RECURSIVE,
};

void f(void)
{
  int (*a)(const pthread_attr_t *, size_t *) = pthread_attr_getguardsize;
  int (*b)(pthread_attr_t *, size_t) = pthread_attr_setguardsize;
  int (*c)(void) = pthread_getconcurrency;
  int (*e)(int) = pthread_setconcurrency;
  int (*f)(const pthread_mutexattr_t *, int *) = pthread_mutexattr_gettype;
  int (*g)(pthread_mutexattr_t *, int) = pthread_mutexattr_settype;
}
