/* additional POSIX functions */
#include <setjmp.h>

/* _setjmp, _longjmp excluded; obsolete in X7 */

void js(sigjmp_buf *env)
{
  siglongjmp(*env, 42);
}

void ls(void)
{
  sigjmp_buf env;
  if (sigsetjmp(env, 1))
    js(&env);
}
