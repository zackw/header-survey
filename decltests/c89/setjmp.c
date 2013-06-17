#include <setjmp.h>

void j(jmp_buf *env)
{
  longjmp(*env, 42);
}

void l(void)
{
  jmp_buf env;
  /* all allowed usage patterns for setjmp: note we only test 'if',
     usage within a loop control expression is also allowed (we're
     betting that modern compilers won't make that behave differently
     than 'if'). */

  if (setjmp(env))
    ;
  else
    j(&env);

  if (setjmp(env) != 42)
    j(&env);

  if (!setjmp(env))
    j(&env);

  (void) setjmp(env);
}
