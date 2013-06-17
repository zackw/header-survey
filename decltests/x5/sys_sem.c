#include <sys/sem.h>

#define NO_INCLUDE_SYS_IPC_H
#include "sys_ipc.c"

int c_sem[] = {
  SEM_UNDO,
  GETNCNT,
  GETPID,
  GETVAL,
  GETALL,
  GETZCNT,
  SETVAL,
  SETALL
};

void f_sem(struct semid_ds *aa, key_t cc)
{
  struct ipc_perm *a = &aa->sem_perm;
  unsigned short   b =  aa->sem_nsems; /* may not actually be unsigned short */
  time_t          *c = &aa->sem_otime;
  time_t          *d = &aa->sem_ctime;

  struct sembuf   bb;
  unsigned short  *e = &bb.sem_num;
  short           *f = &bb.sem_op;
  short           *g = &bb.sem_flg;

  /* http://pubs.opengroup.org/onlinepubs/7908799/xsh/syssem.h.html
     describes an "anonymous structure" that "represents" a semaphore,
     but as far as I can tell this structure is not actually supposed
     to be defined in sem.h; it's only a characterization of the
     various datums that semctl() can retrieve.

     The optional fourth argument to semctl() is defined as "of type
     _union semun_" but as far as I can tell that's a mis-characterization;
     it should work just as well to pass any of its members.  */

  int h = semget(cc, 1, IPC_CREAT);
  int i = semctl(h, 1, IPC_STAT, aa);
  int j = semop(h, &bb, (size_t)1);
}
