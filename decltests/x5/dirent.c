#include <dirent.h>

void f(const char *aa, long int bb)
{
  struct dirent cc;
  ino_t *ccdi = &cc.d_ino;
  char  *ccdn =  cc.d_name;
  struct dirent *dd;
  DIR *ee = opendir(aa);

  struct dirent *a;
  int b;
  long int c;
  int d;

  a = readdir(ee);
  b = readdir_r(ee, &cc, &dd);
  rewinddir(ee);
  seekdir(ee, bb);
  c = telldir(ee);
  d = closedir(ee);
}
