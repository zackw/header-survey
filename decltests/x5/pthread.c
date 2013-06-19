#include <pthread.h>

void cleanup(void *unused)
{}

int xx[] = {
  PTHREAD_CANCEL_ASYNCHRONOUS,
  PTHREAD_CANCEL_ENABLE,
  PTHREAD_CANCEL_DEFERRED,
  PTHREAD_CANCEL_DISABLE,
  PTHREAD_CREATE_DETACHED,
  PTHREAD_CREATE_JOINABLE,
  PTHREAD_EXPLICIT_SCHED,
  PTHREAD_INHERIT_SCHED,
  PTHREAD_PROCESS_SHARED,
  PTHREAD_PROCESS_PRIVATE,
};

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
  void *xk = PTHREAD_CANCELED;

  int   (*aa)(void (*)(void), void (*)(void), void(*)(void)) = pthread_atfork;
  int   (*ab)(pthread_attr_t *) = pthread_attr_destroy;
  int   (*ac)(const pthread_attr_t *, int *) = pthread_attr_getdetachstate;
  int   (*ad)(const pthread_attr_t *, struct sched_param *)
    = pthread_attr_getschedparam;
  int   (*ae)(pthread_attr_t *) = pthread_attr_init;
  int   (*af)(pthread_attr_t *, int) = pthread_attr_setdetachstate;
  int   (*ag)(pthread_attr_t *, const struct sched_param *)
    = pthread_attr_setschedparam;
  int   (*ah)(pthread_t) = pthread_cancel;
  int   (*ai)(pthread_cond_t *) = pthread_cond_broadcast;
  int   (*aj)(pthread_cond_t *) = pthread_cond_destroy;
  int   (*ak)(pthread_cond_t *, const pthread_condattr_t *) = pthread_cond_init;
  int   (*al)(pthread_cond_t *) = pthread_cond_signal;
  int   (*am)(pthread_cond_t *, pthread_mutex_t *, const struct timespec *)
    = pthread_cond_timedwait;
  int   (*an)(pthread_cond_t *, pthread_mutex_t *) = pthread_cond_wait;
  int   (*ao)(pthread_condattr_t *) = pthread_condattr_destroy;
  int   (*ap)(pthread_condattr_t *) = pthread_condattr_init;
  int   (*aq)(pthread_t *, const pthread_attr_t *, void *(*)(void *), void *)
    = pthread_create;
  int   (*ar)(pthread_t) = pthread_detach;
  int   (*as)(pthread_t, pthread_t) = pthread_equal;
  void  (*at)(void *) = pthread_exit;
  void *(*au)(pthread_key_t) = pthread_getspecific;
  int   (*av)(pthread_t, void **) = pthread_join;
  int   (*aw)(pthread_key_t *, void (*)(void *)) = pthread_key_create;
  int   (*ax)(pthread_key_t) = pthread_key_delete;
  int   (*ay)(pthread_mutex_t *) = pthread_mutex_destroy;
  int   (*az)(pthread_mutex_t *, const pthread_mutexattr_t *)
    = pthread_mutex_init;
  int   (*ba)(pthread_mutex_t *) = pthread_mutex_lock;
  int   (*bb)(pthread_mutex_t *) = pthread_mutex_trylock;
  int   (*bc)(pthread_mutex_t *) = pthread_mutex_unlock;
  int   (*bd)(pthread_mutexattr_t *) = pthread_mutexattr_destroy;
  int   (*be)(pthread_mutexattr_t *) = pthread_mutexattr_init;
  int   (*bf)(pthread_once_t *, void (*)(void)) = pthread_once;
  int   (*bg)(pthread_rwlock_t *) = pthread_rwlock_destroy;
  int   (*bh)(pthread_rwlock_t *, const pthread_rwlockattr_t *)
    = pthread_rwlock_init;
  int   (*bi)(pthread_rwlock_t *) = pthread_rwlock_rdlock;
  int   (*bj)(pthread_rwlock_t *) = pthread_rwlock_tryrdlock;
  int   (*bk)(pthread_rwlock_t *) = pthread_rwlock_trywrlock;
  int   (*bl)(pthread_rwlock_t *) = pthread_rwlock_unlock;
  int   (*bm)(pthread_rwlock_t *) = pthread_rwlock_wrlock;
  int   (*bn)(pthread_rwlockattr_t *) = pthread_rwlockattr_destroy;
  int   (*bo)(pthread_rwlockattr_t *) = pthread_rwlockattr_init;
  pthread_t (*bp)(void) = pthread_self;
  int   (*bq)(int, int *) = pthread_setcancelstate;
  int   (*br)(int, int *) = pthread_setcanceltype;
  int   (*bs)(pthread_key_t, const void *) = pthread_setspecific;
  void  (*bt)(void) = pthread_testcancel;

  /* pthread_cleanup_push/pop are macros which must be paired correctly. */
  pthread_cleanup_push(cleanup, (void *)0);
  pthread_cleanup_pop(1);
}
