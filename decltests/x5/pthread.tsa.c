/* thread stack controls */
#include <pthread.h>

void f(void)
{
  int (*a)(const pthread_attr_t *, void **) = pthread_attr_getstackaddr;
  int (*b)(const pthread_attr_t *, size_t *) = pthread_attr_getstacksize;
  int (*c)(pthread_attr_t *, void *) = pthread_attr_setstackaddr;
  int (*d)(pthread_attr_t *, size_t) = pthread_attr_setstacksize;
}
