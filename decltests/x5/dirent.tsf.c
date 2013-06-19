/* <code>readdir_r</code> */
#include <dirent.h>

void f(DIR *aa)
{
  struct dirent a, *b;
  int c = readdir_r(aa, &a, &b);
}
