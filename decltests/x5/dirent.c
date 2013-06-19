#include <dirent.h>

void f(const char *aa)
{
  struct dirent cc;
  char *ccdn = cc.d_name;

  DIR *ee = opendir(aa);
  struct dirent *a = readdir(ee);
  int b = closedir(ee);
  rewinddir(ee);
}
