/* baseline */
#include <semaphore.h>

void f(const char *aa, mode_t cc, unsigned int dd)
{
  sem_t *a = sem_open(aa, 0);
  sem_t *c = SEM_FAILED;
  sem_t d;
  int e = sem_init(&d, 0, dd);

  int f = sem_post(a);
  int g = sem_trywait(&d);
  int h = sem_wait(&d);

  int i;
  int j = sem_getvalue(a, &i);
  int k = sem_close(a);
  int l = sem_destroy(&d);
  int m = sem_unlink(aa);
}

/* semaphore.h may not provide the O_ constants of itself */
#include <fcntl.h>

void g(const char *bb, mode_t cc, unsigned int dd)
{
  sem_t *b = sem_open(bb, O_CREAT|O_EXCL, cc, dd);
}
