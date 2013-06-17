/* additional POSIX error constants */
#include <errno.h>

/* ENODATA, ENOSR, ENOSTR, ETIME excluded - obsolescent in X7 */

void fn(void)
{
  errno = E2BIG;
  errno = EACCES;
  errno = EADDRINUSE;
  errno = EADDRNOTAVAIL;
  errno = EAFNOSUPPORT;
  errno = EAGAIN;
  errno = EALREADY;
  errno = EBADF;
  errno = EBADMSG;
  errno = EBUSY;
  errno = ECANCELED;
  errno = ECHILD;
  errno = ECONNABORTED;
  errno = ECONNREFUSED;
  errno = ECONNRESET;
  errno = EDEADLK;
  errno = EDESTADDRREQ;
  errno = EDQUOT;
  errno = EEXIST;
  errno = EFAULT;
  errno = EFBIG;
  errno = EHOSTUNREACH;
  errno = EIDRM;
  errno = EINPROGRESS;
  errno = EINTR;
  errno = EINVAL;
  errno = EIO;
  errno = EISCONN;
  errno = EISDIR;
  errno = ELOOP;
  errno = EMFILE;
  errno = EMLINK;
  errno = EMSGSIZE;
  errno = EMULTIHOP;
  errno = ENAMETOOLONG;
  errno = ENETDOWN;
  errno = ENETUNREACH;
  errno = ENFILE;
  errno = ENOBUFS;
  errno = ENODEV;
  errno = ENOENT;
  errno = ENOEXEC;
  errno = ENOLCK;
  errno = ENOLINK;
  errno = ENOMEM;
  errno = ENOMSG;
  errno = ENOPROTOOPT;
  errno = ENOSPC;
  errno = ENOSYS;
  errno = ENOTCONN;
  errno = ENOTDIR;
  errno = ENOTEMPTY;
  errno = ENOTSOCK;
  errno = ENOTSUP;
  errno = ENOTTY;
  errno = ENXIO;
  errno = EOPNOTSUPP;
  errno = EOVERFLOW;
  errno = EPERM;
  errno = EPIPE;
  errno = EPROTO;
  errno = EPROTONOSUPPORT;
  errno = EPROTOTYPE;
  errno = EROFS;
  errno = ESPIPE;
  errno = ESRCH;
  errno = ESTALE;
  errno = ETIMEDOUT;
  errno = ETXTBSY;
  errno = EWOULDBLOCK;
  errno = EXDEV;
}
