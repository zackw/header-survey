/* XSI: features */
#include <dirent.h>

void f(DIR *aa)
{
  struct dirent cc;
  ino_t *ccdi = &cc.d_ino;
  ino_t dd; /* confirm a complete type */

  long a = telldir(aa);
  seekdir(aa, a);
}