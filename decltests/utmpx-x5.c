/* baseline */
#include <utmpx.h>

short cc[] = {
  EMPTY,
  BOOT_TIME,
  OLD_TIME,
  NEW_TIME,
  USER_PROCESS,
  INIT_PROCESS,
  LOGIN_PROCESS,
  DEAD_PROCESS,
};

void f(struct utmpx *uu)
{
  char  *uuu =  uu->ut_user;
  char  *uui =  uu->ut_id;
  char  *uul =  uu->ut_line;
  pid_t *uup = &uu->ut_pid;
  short *uut = &uu->ut_type;
  /* For the sake of on-disk compatibility, ut_tv may not actually be a
     'struct timeval'. */
  struct timeval tt;
  tt.tv_sec  = uu->ut_tv.tv_sec;
  tt.tv_usec = uu->ut_tv.tv_usec;

  struct utmpx *a = getutxent();
  struct utmpx *b = getutxid(a);
  struct utmpx *c = getutxline(a);
  struct utmpx *d = pututxline(a);
  setutxent();
  endutxent();
}
