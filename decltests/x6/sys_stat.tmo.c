/* optional: support for typed memory objects */
#include <sys/stat.h>

void smacros(struct stat *aa)
{
  int a = S_TYPEISTMO(aa);
}
