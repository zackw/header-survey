/* baseline */
#include <sys/msg.h>

#define NO_INCLUDE_SYS_IPC_H
#include "ipc-x5.c"

void f_msg(struct msqid_ds *aa, key_t bb, const void *cc, void *dd,
           size_t ee, long ff)
{
  struct ipc_perm *a = &aa->msg_perm;
  msgqnum_t       *b = &aa->msg_qnum;
  msglen_t        *c = &aa->msg_qbytes;
  pid_t           *d = &aa->msg_lspid;
  pid_t           *e = &aa->msg_lrpid;
  time_t          *f = &aa->msg_stime;
  time_t          *g = &aa->msg_rtime;
  time_t          *h = &aa->msg_ctime;

  int i = msgget(bb, IPC_CREAT);
  int j = msgctl(i, IPC_STAT, aa);
  int k = msgsnd(i, cc, ee, IPC_NOWAIT);
  int l = msgrcv(i, dd, ee, ff, MSG_NOERROR);
}
