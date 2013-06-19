/* XSI: <code>ucontext_t</code> and <code>mcontext_t</code> */
#include <signal.h>

/* In Issue 5, ucontext_t and mcontext_t are defined in <ucontext.h>,
   but (with XSI) are also required to be visible in <signal.h>.
   Issue 6 obsoletes the functions declared in <ucontext.h>, and
   Issue 7 moves the official location of ucontext_t and mcontext_t to
   <signal.h>.  Some OSes (notably OSX) jumped the gun on obsolescing
   the entire <ucontext.h> header, so it is convenient for us to
   reassign validation of ucontext_t to <signal.h>. */

void t(void)
{
  mcontext_t mc; /* contents wholly system-specific */
  ucontext_t uc;
  ucontext_t **ucu = &uc.uc_link;
  sigset_t    *ucs = &uc.uc_sigmask;
  stack_t     *uct = &uc.uc_stack;
  mcontext_t  *ucm = &uc.uc_mcontext;
}
