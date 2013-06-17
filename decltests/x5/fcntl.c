#include <fcntl.h>

void f(void)
{
  int
    a = F_DUPFD,
    b = F_GETFD,
    c = F_GETFL,
    d = F_SETFL,
    e = F_GETLK,
    f = F_SETLK,
    g = F_SETLKW,

    h = FD_CLOEXEC,

    i = F_RDLCK,
    j = F_WRLCK,
    k = F_UNLCK,

    l = SEEK_SET,
    m = SEEK_CUR,
    n = SEEK_END,

    o = O_CREAT,
    p = O_EXCL,
    q = O_NOCTTY,
    r = O_TRUNC,

    s = O_APPEND,
    t = O_DSYNC,
    u = O_NONBLOCK,
    v = O_RSYNC,
    w = O_SYNC,

    x = O_RDONLY,
    y = O_WRONLY,
    z = O_RDWR,

    sa = S_IFMT,
    sb = S_IFBLK,
    sc = S_IFCHR,
    sd = S_IFIFO,
    se = S_IFREG,
    sf = S_IFDIR,
    sg = S_IFLNK,

    sh = S_IRWXU,
    si = S_IRUSR,
    sj = S_IWUSR,
    sk = S_IXUSR,

    sl = S_IRWXG,
    sm = S_IRGRP,
    sn = S_IWGRP,
    so = S_IXGRP,

    st = S_IRWXO,
    su = S_IROTH,
    sv = S_IWOTH,
    sw = S_IXOTH,

    sx = S_ISUID,
    sy = S_ISGID,
    sz = S_ISVTX;

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
