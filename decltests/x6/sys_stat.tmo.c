/* typed memory object support */
#include <sys/stat.h>

void smacros(struct stat *aa)
{
  int a = S_TYPEISTMO(aa);
}
