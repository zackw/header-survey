#include <semaphore.h>

sem_t *xx[] = {
  SEM_FAILED,
};

void f(void)
{
  int    (*a)(sem_t *) = sem_close;
  int    (*b)(sem_t *) = sem_destroy;
  int    (*c)(sem_t *, int *) = sem_getvalue;
  int    (*d)(sem_t *, int, unsigned) = sem_init;
  sem_t *(*e)(const char *, int, ...) = sem_open;
  int    (*f)(sem_t *) = sem_post;
  int    (*g)(sem_t *) = sem_trywait;
  int    (*h)(const char *) = sem_unlink;
  int    (*i)(sem_t *) = sem_wait;
}
