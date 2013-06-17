/* baseline */
#include <sys/shm.h>

#define NO_INCLUDE_SYS_IPC_H
#include "ipc-x5.c"

int c_shm[] = {
  SHM_RDONLY,
  SHM_RND
};

void f_shm(struct shmid_ds *aa, key_t bb)
{
  struct ipc_perm *a = &aa->shm_perm;
  size_t          *b = &aa->shm_segsz;
  pid_t           *c = &aa->shm_lpid;
  pid_t           *d = &aa->shm_cpid;
  shmatt_t        *e = &aa->shm_nattch;
  time_t          *f = &aa->shm_atime;
  time_t          *g = &aa->shm_dtime;
  time_t          *h = &aa->shm_ctime;

  int i   = shmget(bb, 1024*1024*12, IPC_CREAT);
  int j   = shmctl(bb, IPC_STAT, aa);
  void *k = shmat(bb, 0, SHM_RDONLY);
  int l   = shmdt(k);

  /* Not guaranteed to be compile-time constant, e.g. it might be
     #defined to a call to getpagesize(). */
  int m = SHMLBA;
}
