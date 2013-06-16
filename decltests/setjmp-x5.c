/* SUSv2 additions */
#include <setjmp.h>

void js(sigjmp_buf *env)
{
  siglongjmp(*env, 42);
}

void j_(jmp_buf *env)
{
  _longjmp(*env, 42);
}

void ls(void)
{
  sigjmp_buf env;
  if (sigsetjmp(env, 1))
    js(&env);
}

void l_(void)
{
  jmp_buf env;
  if (_setjmp(env))
    j_(&env);
}
