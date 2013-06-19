/* optional: limit constants for threads */
#include <limits.h>

/* minimum-maximum */
#if !defined _POSIX_THREAD_DESTRUCTOR_ITERATIONS || _POSIX_THREAD_DESTRUCTOR_ITERATIONS < 4
#error "_POSIX_THREAD_DESTRUCTOR_ITERATIONS"
#endif
#if !defined _POSIX_THREAD_KEYS_MAX || _POSIX_THREAD_KEYS_MAX < 128
#error "_POSIX_THREAD_KEYS_MAX"
#endif
#if !defined _POSIX_THREAD_THREADS_MAX || _POSIX_THREAD_THREADS_MAX < 64
#error "_POSIX_THREAD_THREADS_MAX"
#endif

/* not necessarily defined */
#if defined PTHREAD_DESTRUCTOR_ITERATIONS && \
     PTHREAD_DESTRUCTOR_ITERATIONS < _POSIX_THREAD_DESTRUCTOR_ITERATIONS
#error "PTHREAD_DESTRUCTOR_ITERATIONS"
#endif
#if defined PTHREAD_KEYS_MAX && PTHREAD_KEYS_MAX < _POSIX_THREAD_KEYS_MAX
#error "PTHREAD_KEYS_MAX"
#endif
#if defined PTHREAD_STACK_MIN && PTHREAD_STACK_MIN < 0
#error "PTHREAD_STACK_MIN"
#endif
#if defined PTHREAD_THREADS_MAX && \
     PTHREAD_THREADS_MAX < _POSIX_THREAD_THREADS_MAX
#error "PTHREAD_THREADS_MAX"
#endif

int dummy; /* avoid error for empty source file */
