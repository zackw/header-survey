#include <fcntl.h>

int cc[] = {
  F_DUPFD,
  F_GETFD,
  F_SETFD,
  F_GETFL,
  F_SETFL,
  F_GETLK,
  F_SETLK,
  F_SETLKW,

  FD_CLOEXEC,

  F_RDLCK,
  F_WRLCK,
  F_UNLCK,

  O_CREAT,
  O_EXCL,
  O_NOCTTY,
  O_TRUNC,

  O_APPEND,
  O_NONBLOCK,
  O_SYNC,

  O_ACCMODE,
  O_RDONLY,
  O_WRONLY,
  O_RDWR,
};

void f(void)
{
  struct flock ll;
  short *llt = &ll.l_type;
  short *llw = &ll.l_whence;
  off_t *lls = &ll.l_start;
  off_t *lll = &ll.l_len;
  pid_t *llp = &ll.l_pid;

  int fa = creat("name1", S_IRWXU|S_IRWXG|S_IRWXO);
  int fb = open("name2", O_RDONLY);
  int fc = open("name3", O_RDWR|O_CREAT|O_EXCL, 0666);

  int fd = fcntl(fa, F_DUPFD, 0);
  int fe = fcntl(fd, F_SETFD, FD_CLOEXEC);

  int ff = fcntl(fb, F_GETFL);
  int fg = fcntl(fb, F_SETFL, ff | O_NONBLOCK);

  int fh = fcntl(fc, F_GETLK, &ll);
}
