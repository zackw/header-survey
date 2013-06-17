#ifndef NO_INCLUDE_SYS_IPC_H
#include <sys/ipc.h>
#endif

void f_ipc(struct ipc_perm *ip)
{
  uid_t  *a = &ip->uid;
  gid_t  *b = &ip->gid;
  uid_t  *c = &ip->cuid;
  uid_t  *d = &ip->cgid;
  mode_t  e =  ip->mode;  /* specified as mode_t, but not actually on
                             some systems */

  int
    f = IPC_CREAT,
    g = IPC_EXCL,
    h = IPC_NOWAIT,
    i = IPC_RMID,
    j = IPC_SET,
    k = IPC_STAT;

  key_t
    l = IPC_PRIVATE,
    m = ftok("file", 'k');
}
