#include <unistd.h>

/* We make no attempt to audit the _POSIX_* feature reporting macros.
   There are too many of them, their interaction is too complex, and
   the rules change radically in each Issue. */

/* Removed in Issue 6 or 7:
   _POSIX2_C_VERSION
   _SC_PASS_MAX

*/

#ifndef _POSIX_VERSION
#error "_POSIX_VERSION"
#endif
#ifndef _POSIX2_VERSION
#error "_POSIX2_VERSION"
#endif

/* Constants used in APIs */

void *pc = NULL;

int ic[] = {
  F_OK, R_OK, W_OK, X_OK,

  SEEK_SET, SEEK_CUR, SEEK_END,

  _CS_PATH,

  _PC_ASYNC_IO,
  _PC_CHOWN_RESTRICTED,
  _PC_FILESIZEBITS,
  _PC_LINK_MAX,
  _PC_MAX_CANON,
  _PC_MAX_INPUT,
  _PC_NAME_MAX,
  _PC_NO_TRUNC,
  _PC_PATH_MAX,
  _PC_PIPE_BUF,
  _PC_PRIO_IO,
  _PC_SYNC_IO,
  _PC_VDISABLE,

  _SC_2_C_BIND,
  _SC_2_C_DEV,
  _SC_2_FORT_DEV,
  _SC_2_FORT_RUN,
  _SC_2_LOCALEDEF,
  _SC_2_SW_DEV,
  _SC_2_UPE,
  _SC_2_VERSION,
  _SC_AIO_LISTIO_MAX,
  _SC_AIO_MAX,
  _SC_AIO_PRIO_DELTA_MAX,
  _SC_ARG_MAX,
  _SC_ASYNCHRONOUS_IO,
  _SC_ATEXIT_MAX,
  _SC_BC_BASE_MAX,
  _SC_BC_DIM_MAX,
  _SC_BC_SCALE_MAX,
  _SC_BC_STRING_MAX,
  _SC_CHILD_MAX,
  _SC_CLK_TCK,
  _SC_COLL_WEIGHTS_MAX,
  _SC_DELAYTIMER_MAX,
  _SC_EXPR_NEST_MAX,
  _SC_FSYNC,
  _SC_GETGR_R_SIZE_MAX,
  _SC_GETPW_R_SIZE_MAX,
  _SC_IOV_MAX,
  _SC_JOB_CONTROL,
  _SC_LINE_MAX,
  _SC_LOGIN_NAME_MAX,
  _SC_MAPPED_FILES,
  _SC_MEMLOCK,
  _SC_MEMLOCK_RANGE,
  _SC_MEMORY_PROTECTION,
  _SC_MESSAGE_PASSING,
  _SC_MQ_OPEN_MAX,
  _SC_MQ_PRIO_MAX,
  _SC_NGROUPS_MAX,
  _SC_OPEN_MAX,
  _SC_PAGESIZE,
  _SC_PAGE_SIZE,
  _SC_PRIORITIZED_IO,
  _SC_PRIORITY_SCHEDULING,
  _SC_REALTIME_SIGNALS,
  _SC_RE_DUP_MAX,
  _SC_RTSIG_MAX,
  _SC_SAVED_IDS,
  _SC_SEMAPHORES,
  _SC_SEM_NSEMS_MAX,
  _SC_SEM_VALUE_MAX,
  _SC_SHARED_MEMORY_OBJECTS,
  _SC_SIGQUEUE_MAX,
  _SC_STREAM_MAX,
  _SC_SYNCHRONIZED_IO,
  _SC_THREADS,
  _SC_THREAD_ATTR_STACKADDR,
  _SC_THREAD_ATTR_STACKSIZE,
  _SC_THREAD_DESTRUCTOR_ITERATIONS,
  _SC_THREAD_KEYS_MAX,
  _SC_THREAD_PRIORITY_SCHEDULING,
  _SC_THREAD_PRIO_INHERIT,
  _SC_THREAD_PRIO_PROTECT,
  _SC_THREAD_PROCESS_SHARED,
  _SC_THREAD_SAFE_FUNCTIONS,
  _SC_THREAD_STACK_MIN,
  _SC_THREAD_THREADS_MAX,
  _SC_TIMERS,
  _SC_TIMER_MAX,
  _SC_TTY_NAME_MAX,
  _SC_TZNAME_MAX,
  _SC_VERSION,
  _SC_XBS5_ILP32_OFF32,
  _SC_XBS5_ILP32_OFFBIG,
  _SC_XBS5_LP64_OFF64,
  _SC_XBS5_LPBIG_OFFBIG,
  _SC_XOPEN_CRYPT,
  _SC_XOPEN_ENH_I18N,
  _SC_XOPEN_LEGACY,
  _SC_XOPEN_REALTIME,
  _SC_XOPEN_REALTIME_THREADS,
  _SC_XOPEN_SHM,
  _SC_XOPEN_UNIX,
  _SC_XOPEN_VERSION,
};

/* these have definite values */

#if !defined STDIN_FILENO || STDIN_FILENO != 0
#error "STDIN_FILENO"
#endif
#if !defined STDOUT_FILENO || STDOUT_FILENO != 1
#error "STDOUT_FILENO"
#endif
#if !defined STDERR_FILENO || STDERR_FILENO != 2
#error "STDERR_FILENO"
#endif

/* usable types */
size_t ta;
ssize_t tb;
uid_t tc;
gid_t td;
off_t te;
pid_t tf;
intptr_t th;

/* function declarations removed in Issue 6 or 7:
   brk
   chroot
   cuserid
   ctermid
   getdtablesize
   getpagesize
   getpass
   getwd
   sbrk
*/

void f(void)
{
  int          (*aa)(const char *, int) = access;
  unsigned     (*ab)(unsigned) = alarm;
  int          (*ad)(const char *) = chdir;
  int          (*af)(const char *, uid_t, gid_t) = chown;
  int          (*ag)(int) = close;
  size_t       (*ah)(int, char *, size_t) = confstr;
  int          (*al)(int) = dup;
  int          (*am)(int, int) = dup2;
  int          (*ao)(const char *, const char *, ...) = execl;
  int          (*ap)(const char *, const char *, ...) = execle;
  int          (*aq)(const char *, const char *, ...) = execlp;
  int          (*ar)(const char *, char *const []) = execv;
  int          (*as)(const char *, char *const [], char *const []) = execve;
  int          (*at)(const char *, char *const []) = execvp;
  void         (*au)(int) = _exit;
  int          (*av)(int, uid_t, gid_t) = fchown;
  pid_t        (*ay)(void) = fork;
  long         (*az)(int, int) = fpathconf;
  int          (*bb)(int, off_t) = ftruncate;
  char        *(*bc)(char *, size_t) = getcwd;
  gid_t        (*be)(void) = getegid;
  uid_t        (*bf)(void) = geteuid;
  gid_t        (*bg)(void) = getgid;
  int          (*bh)(int, gid_t []) = getgroups;
  char        *(*bj)(void) = getlogin;
  int          (*bk)(char *, size_t) = getlogin_r;
  int          (*bl)(int, char * const [], const char *) = getopt;
  pid_t        (*bp)(void) = getpgrp;
  pid_t        (*bq)(void) = getpid;
  pid_t        (*br)(void) = getppid;
  uid_t        (*bt)(void) = getuid;
  int          (*bv)(int) = isatty;
  int          (*bx)(const char *, const char *) = link;
  off_t        (*bz)(int, off_t, int) = lseek;
  long         (*cb)(const char *, int) = pathconf;
  int          (*cc)(void) = pause;
  int          (*cd)(int [2]) = pipe;
  ssize_t      (*ch)(int, void *, size_t) = read;
  ssize_t      (*ci)(const char *, char *, size_t) = readlink;
  int          (*cj)(const char *) = rmdir;
  int          (*cl)(gid_t) = setgid;
  int          (*cm)(pid_t, pid_t) = setpgid;
  pid_t        (*cq)(void) = setsid;
  int          (*cr)(uid_t) = setuid;
  unsigned     (*cs)(unsigned) = sleep;
  int          (*cu)(const char *, const char *) = symlink;
  long         (*cw)(int) = sysconf;
  pid_t        (*cx)(int) = tcgetpgrp;
  int          (*cy)(int, pid_t) = tcsetpgrp;
  char        *(*da)(int) = ttyname;
  int          (*db)(int, char *, size_t) = ttyname_r;
  int          (*dd)(const char *) = unlink;
  ssize_t      (*dg)(int, const void *, size_t) = write;

  char *a = optarg;
  int b = opterr, c = optind, d = optopt;
}
