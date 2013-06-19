/* optional: thread stack controls */
#include <pthread.h>

void f(void)
{
  int (*a)(const pthread_attr_t *, void **, size_t *) = pthread_attr_getstack;
  int (*b)(pthread_attr_t *, void *, size_t) = pthread_attr_setstack;
}
