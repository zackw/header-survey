/* baseline */
#include <pthread.h>

void cleanup(void *unused)
{}

void f(void)
{
  pthread_attr_t xa;
  pthread_cond_t xb = PTHREAD_COND_INITIALIZER;
  pthread_condattr_t xc;
  pthread_key_t xd;
  pthread_mutex_t xe = PTHREAD_MUTEX_INITIALIZER;
  pthread_mutexattr_t xf;
  pthread_once_t xg = PTHREAD_ONCE_INIT;
  pthread_rwlock_t xh = PTHREAD_RWLOCK_INITIALIZER;
  pthread_rwlockattr_t xi;
  pthread_t xj;

  int
    ya = PTHREAD_CANCEL_ASYNCHRONOUS,
    yb = PTHREAD_CANCEL_ENABLE,
    yc = PTHREAD_CANCEL_DEFERRED,
    yd = PTHREAD_CANCEL_DISABLE,
    ye = PTHREAD_CANCELED,
    yf = PTHREAD_CREATE_DETACHED,
    yg = PTHREAD_CREATE_JOINABLE,
    yh = PTHREAD_EXPLICIT_SCHED,
    yi = PTHREAD_INHERIT_SCHED,
    yj = PTHREAD_MUTEX_DEFAULT,
    yk = PTHREAD_MUTEX_ERRORCHECK,
    yl = PTHREAD_MUTEX_NORMAL,
    ym = PTHREAD_MUTEX_RECURSIVE,
    yn = PTHREAD_PRIO_INHERIT,
    yo = PTHREAD_PRIO_NONE,
    yp = PTHREAD_PRIO_PROTECT,
    yq = PTHREAD_PROCESS_SHARED,
    yr = PTHREAD_PROCESS_PRIVATE,
    ys = PTHREAD_SCOPE_PROCESS,
    yt = PTHREAD_SCOPE_SYSTEM;

  /* We take function pointers to all the pthread_* functions instead of
     calling them because this made it easier to copy and paste the
     giant list from the spec. */

  int   (*aa)(pthread_attr_t *) = pthread_attr_destroy;
  int   (*ab)(const pthread_attr_t *, int *) = pthread_attr_getdetachstate;
  int   (*ac)(const pthread_attr_t *, size_t *) = pthread_attr_getguardsize;
  int   (*ad)(const pthread_attr_t *, int *) = pthread_attr_getinheritsched;
  int   (*ae)(const pthread_attr_t *, struct sched_param *)
    = pthread_attr_getschedparam;
  int   (*af)(const pthread_attr_t *, int *) = pthread_attr_getschedpolicy;
  int   (*ag)(const pthread_attr_t *, int *) = pthread_attr_getscope;
  int   (*ah)(const pthread_attr_t *, void **) = pthread_attr_getstackaddr;
  int   (*ai)(const pthread_attr_t *, size_t *) = pthread_attr_getstacksize;
  int   (*aj)(pthread_attr_t *) = pthread_attr_init;
  int   (*ak)(pthread_attr_t *, int) = pthread_attr_setdetachstate;
  int   (*al)(pthread_attr_t *, size_t) = pthread_attr_setguardsize;
  int   (*am)(pthread_attr_t *, int) = pthread_attr_setinheritsched;
  int   (*an)(pthread_attr_t *, const struct sched_param *)
    = pthread_attr_setschedparam;
  int   (*ao)(pthread_attr_t *, int) = pthread_attr_setschedpolicy;
  int   (*ap)(pthread_attr_t *, int) = pthread_attr_setscope;
  int   (*aq)(pthread_attr_t *, void *) = pthread_attr_setstackaddr;
  int   (*ar)(pthread_attr_t *, size_t) = pthread_attr_setstacksize;
  int   (*as)(pthread_t) = pthread_cancel;
  int   (*av)(pthread_cond_t *) = pthread_cond_broadcast;
  int   (*aw)(pthread_cond_t *) = pthread_cond_destroy;
  int   (*ax)(pthread_cond_t *, const pthread_condattr_t *) = pthread_cond_init;
  int   (*ay)(pthread_cond_t *) = pthread_cond_signal;
  int   (*az)(pthread_cond_t *, pthread_mutex_t *, const struct timespec *)
    = pthread_cond_timedwait;
  int   (*ba)(pthread_cond_t *, pthread_mutex_t *) = pthread_cond_wait;
  int   (*bb)(pthread_condattr_t *) = pthread_condattr_destroy;
  int   (*bc)(const pthread_condattr_t *, int *) = pthread_condattr_getpshared;
  int   (*bd)(pthread_condattr_t *) = pthread_condattr_init;
  int   (*be)(pthread_condattr_t *, int) = pthread_condattr_setpshared;
  int   (*bf)(pthread_t *, const pthread_attr_t *, void *(*)(void *), void *)
    = pthread_create;
  int   (*bg)(pthread_t) = pthread_detach;
  int   (*bh)(pthread_t, pthread_t) = pthread_equal;
  void  (*bi)(void *) = pthread_exit;
  int   (*bj)(void) = pthread_getconcurrency;
  int   (*bk)(pthread_t, int *, struct sched_param *) = pthread_getschedparam;
  void *(*bl)(pthread_key_t) = pthread_getspecific;
  int   (*bm)(pthread_t, void **) = pthread_join;
  int   (*bn)(pthread_key_t *, void (*)(void *)) = pthread_key_create;
  int   (*bo)(pthread_key_t) = pthread_key_delete;
  int   (*bp)(pthread_mutex_t *) = pthread_mutex_destroy;
  int   (*bq)(const pthread_mutex_t *, int *) = pthread_mutex_getprioceiling;
  int   (*br)(pthread_mutex_t *, const pthread_mutexattr_t *)
    = pthread_mutex_init;
  int   (*bs)(pthread_mutex_t *) = pthread_mutex_lock;
  int   (*bt)(pthread_mutex_t *, int, int *) = pthread_mutex_setprioceiling;
  int   (*bu)(pthread_mutex_t *) = pthread_mutex_trylock;
  int   (*bv)(pthread_mutex_t *) = pthread_mutex_unlock;
  int   (*bw)(pthread_mutexattr_t *) = pthread_mutexattr_destroy;
  int   (*bx)(const pthread_mutexattr_t *, int *)
    = pthread_mutexattr_getprioceiling;
  int   (*by)(const pthread_mutexattr_t *, int *)
    = pthread_mutexattr_getprotocol;
  int   (*bz)(const pthread_mutexattr_t *, int *)
    = pthread_mutexattr_getpshared;
  int   (*ca)(const pthread_mutexattr_t *, int *) = pthread_mutexattr_gettype;
  int   (*cb)(pthread_mutexattr_t *) = pthread_mutexattr_init;
  int   (*cc)(pthread_mutexattr_t *, int) = pthread_mutexattr_setprioceiling;
  int   (*cd)(pthread_mutexattr_t *, int) = pthread_mutexattr_setprotocol;
  int   (*ce)(pthread_mutexattr_t *, int) = pthread_mutexattr_setpshared;
  int   (*cf)(pthread_mutexattr_t *, int) = pthread_mutexattr_settype;
  int   (*cg)(pthread_once_t *, void (*)(void)) = pthread_once;
  int   (*ch)(pthread_rwlock_t *) = pthread_rwlock_destroy;
  int   (*ci)(pthread_rwlock_t *, const pthread_rwlockattr_t *)
    = pthread_rwlock_init;
  int   (*cj)(pthread_rwlock_t *) = pthread_rwlock_rdlock;
  int   (*ck)(pthread_rwlock_t *) = pthread_rwlock_tryrdlock;
  int   (*cl)(pthread_rwlock_t *) = pthread_rwlock_trywrlock;
  int   (*cm)(pthread_rwlock_t *) = pthread_rwlock_unlock;
  int   (*cn)(pthread_rwlock_t *) = pthread_rwlock_wrlock;
  int   (*co)(pthread_rwlockattr_t *) = pthread_rwlockattr_destroy;
  int   (*cp)(const pthread_rwlockattr_t *, int *)
    = pthread_rwlockattr_getpshared;
  int   (*cq)(pthread_rwlockattr_t *) = pthread_rwlockattr_init;
  int   (*cr)(pthread_rwlockattr_t *, int) = pthread_rwlockattr_setpshared;
  pthread_t (*cs)(void) = pthread_self;
  int   (*ct)(int, int *) = pthread_setcancelstate;
  int   (*cu)(int, int *) = pthread_setcanceltype;
  int   (*cv)(int) = pthread_setconcurrency;
  int   (*cw)(pthread_t, int, const struct sched_param *)
    = pthread_setschedparam;
  int   (*cx)(pthread_key_t, const void *) = pthread_setspecific;
  void  (*cy)(void) = pthread_testcancel;

  /* pthread_cleanup_push/pop are macros which must be paired correctly. */
  pthread_cleanup_push(cleanup, (void *)0);
  pthread_cleanup_pop(1);
}
