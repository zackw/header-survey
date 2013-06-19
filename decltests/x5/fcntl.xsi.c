/* XSI: features */
#include <fcntl.h>

int cc[] = {
  SEEK_SET,
  SEEK_CUR,
  SEEK_END,

  S_IFMT,
  S_IFBLK,
  S_IFCHR,
  S_IFIFO,
  S_IFREG,
  S_IFDIR,
  S_IFLNK,

  S_IRWXU,
  S_IRUSR,
  S_IWUSR,
  S_IXUSR,

  S_IRWXG,
  S_IRGRP,
  S_IWGRP,
  S_IXGRP,

  S_IRWXO,
  S_IROTH,
  S_IWOTH,
  S_IXOTH,

  S_ISUID,
  S_ISGID,
  S_ISVTX,
};
