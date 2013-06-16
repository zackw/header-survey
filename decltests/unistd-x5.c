/* baseline */
#include <unistd.h>

/* Optionally defined feature-test macros:

   _XOPEN_XPG2, _XOPEN_XPG3, _XOPEN_XPG4, _XOPEN_UNIX

   _POSIX_CHOWN_RESTRICTED, _POSIX_NO_TRUNC, _POSIX_VDISABLE,
   _POSIX_SAVED_IDS, _POSIX_JOB_CONTROL

   _POSIX2_C_BIND, _POSIX2_C_DEV, _POSIX2_CHAR_TERM, _POSIX2_FORT_DEV,
   _POSIX2_FORT_RUN, _POSIX2_LOCALEDEF, _POSIX2_SW_DEV, _POSIX2_UPE,
   _XOPEN_CRYPT, _XOPEN_ENH_I18N, _XOPEN_LEGACY, _XOPEN_REALTIME,
   _XOPEN_REALTIME_THREADS, _XOPEN_SHM, _XBS5_ILP32_OFF32,
   _XBS5_ILP32_OFFBIG, _XBS5_LP64_OFF64, _XBS5_LPBIG_OFFBIG,

   _POSIX_PRIORITIZED_IO

   _POSIX_ASYNC_IO, _POSIX_PRIO_IO, _POSIX_SYNC_IP

*/

/* Definitely defined feature-test macros */

#ifndef _POSIX_VERSION
#error "_POSIX_VERSION"
#endif
#ifndef _POSIX2_VERSION
#error "_POSIX2_VERSION"
#endif
/*??? not defined by glibc 2.17, who are assumed to know what they are doing
#ifndef _POSIX2_C_VERSION
#error "_POSIX2_C_VERSION"
#endif*/
#ifndef _XOPEN_VERSION
#error "_XOPEN_VERSION"
#endif

#ifndef _POSIX_THREADS
#error "_POSIX_THREADS"
#endif
#ifndef _POSIX_THREAD_ATTR_STACKADDR
#error "_POSIX_THREAD_ATTR_STACKADDR"
#endif
#ifndef _POSIX_THREAD_ATTR_STACKSIZE
#error "_POSIX_THREAD_ATTR_STACKSIZE"
#endif
#ifndef _POSIX_THREAD_PROCESS_SHARED
#error "_POSIX_THREAD_PROCESS_SHARED"
#endif
#ifndef _POSIX_THREAD_SAFE_FUNCTIONS
#error "_POSIX_THREAD_SAFE_FUNCTIONS"
#endif

#ifndef _POSIX_FSYNC
#error "_POSIX_FSYNC"
#endif
#ifndef _POSIX_MAPPED_FILES
#error "_POSIX_MAPPED_FILES"
#endif
#ifndef _POSIX_MEMORY_PROTECTION
#error "_POSIX_MEMORY_PROTECTION"
#endif

/* "if this is defined, then these are also defined" */
#ifdef _XOPEN_REALTIME

#ifndef _POSIX_ASYNCHRONOUS_IO
#error "_POSIX_ASYNCHRONOUS_IO"
#endif
#ifndef _POSIX_MEMLOCK
#error "_POSIX_MEMLOCK"
#endif
#ifndef _POSIX_MEMLOCK_RANGE
#error "_POSIX_MEMLOCK_RANGE"
#endif
#ifndef _POSIX_MESSAGE_PASSING
#error "_POSIX_MESSAGE_PASSING"
#endif
#ifndef _POSIX_PRIORITY_SCHEDULING
#error "_POSIX_PRIORITY_SCHEDULING"
#endif
#ifndef _POSIX_REALTIME_SIGNALS
#error "_POSIX_REALTIME_SIGNALS"
#endif
#ifndef _POSIX_SEMAPHORES
#error "_POSIX_SEMAPHORES"
#endif
#ifndef _POSIX_SHARED_MEMORY_OBJECTS
#error "_POSIX_SHARED_MEMORY_OBJECTS"
#endif
#ifndef _POSIX_SYNCHRONIZED_IO
#error "_POSIX_SYNCHRONIZED_IO"
#endif
#ifndef _POSIX_TIMERS
#error "_POSIX_TIMERS"
#endif

#endif

#ifdef _XOPEN_REALTIME_THREADS

#ifndef _POSIX_THREAD_PRIORITY_SCHEDULING
#error "_POSIX_THREAD_PRIORITY_SCHEDULING"
#endif
#ifndef _POSIX_THREAD_PRIO_INHERIT
#error "_POSIX_THREAD_PRIO_INHERIT"
#endif
#ifndef _POSIX_THREAD_PRIO_PROTECT
#error "_POSIX_THREAD_PRIO_PROTECT"
#endif

#endif

/* Constants used in APIs */

void *pc = NULL;

int ic[] = {
  R_OK, W_OK, X_OK, F_OK,

  SEEK_SET, SEEK_CUR, SEEK_END,

  F_LOCK, F_ULOCK, F_TEST, F_TLOCK,

  _CS_PATH,
  _CS_XBS5_ILP32_OFF32_CFLAGS,
  _CS_XBS5_ILP32_OFF32_LDFLAGS,
  _CS_XBS5_ILP32_OFF32_LIBS,
  _CS_XBS5_ILP32_OFF32_LINTFLAGS,
  _CS_XBS5_ILP32_OFFBIG_CFLAGS,
  _CS_XBS5_ILP32_OFFBIG_LDFLAGS,
  _CS_XBS5_ILP32_OFFBIG_LIBS,
  _CS_XBS5_ILP32_OFFBIG_LINTFLAGS,
  _CS_XBS5_LP64_OFF64_CFLAGS,
  _CS_XBS5_LP64_OFF64_LDFLAGS,
  _CS_XBS5_LP64_OFF64_LIBS,
  _CS_XBS5_LP64_OFF64_LINTFLAGS,
  _CS_XBS5_LPBIG_OFFBIG_CFLAGS,
  _CS_XBS5_LPBIG_OFFBIG_LDFLAGS,
  _CS_XBS5_LPBIG_OFFBIG_LIBS,
  _CS_XBS5_LPBIG_OFFBIG_LINTFLAGS,

  _SC_2_C_BIND,
  _SC_2_C_DEV,
  _SC_2_C_VERSION,
  _SC_2_FORT_DEV,
  _SC_2_FORT_RUN,
  _SC_2_LOCALEDEF,
  _SC_2_SW_DEV,
  _SC_2_UPE,
  _SC_2_VERSION,
  _SC_ARG_MAX,
  _SC_AIO_LISTIO_MAX,
  _SC_AIO_MAX,
  _SC_AIO_PRIO_DELTA_MAX,
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
  /* _SC_PASS_MAX (LEGACY) */
  _SC_PRIORITIZED_IO,
  _SC_PRIORITY_SCHEDULING,
  _SC_RE_DUP_MAX,

  _SC_REALTIME_SIGNALS,
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
  _SC_XOPEN_VERSION,
  _SC_XOPEN_CRYPT,
  _SC_XOPEN_ENH_I18N,
  _SC_XOPEN_SHM,
  _SC_XOPEN_UNIX,
  _SC_XOPEN_XCU_VERSION,
  _SC_XOPEN_LEGACY,
  _SC_XOPEN_REALTIME,
  _SC_XOPEN_REALTIME_THREADS,
  _SC_XBS5_ILP32_OFF32,
  _SC_XBS5_ILP32_OFFBIG,
  _SC_XBS5_LP64_OFF64,
  _SC_XBS5_LPBIG_OFFBIG,

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
useconds_t tg;
intptr_t th;

/* declarations - there are lots, so we use the same technique as for
   pthread.h */

void f(void)
{
  int          (*aa)(const char *, int) = access;
  unsigned     (*ab)(unsigned) = alarm;
  int          (*ac)(void *) = brk;
  int          (*ad)(const char *) = chdir;
/*int          (*ae)(const char *) = chroot; (LEGACY) */
  int          (*af)(const char *, uid_t, gid_t) = chown;
  int          (*ag)(int) = close;
  size_t       (*ah)(int, char *, size_t) = confstr;
  char        *(*ai)(const char *, const char *) = crypt;
  char        *(*aj)(char *) = ctermid;
/*char        *(*ak)(char *s) = cuserid; (LEGACY) */
  int          (*al)(int) = dup;
  int          (*am)(int, int) = dup2;
  void         (*an)(char[64], int) = encrypt;
  int          (*ao)(const char *, const char *, ...) = execl;
  int          (*ap)(const char *, const char *, ...) = execle;
  int          (*aq)(const char *, const char *, ...) = execlp;
  int          (*ar)(const char *, char *const []) = execv;
  int          (*as)(const char *, char *const [], char *const []) = execve;
  int          (*at)(const char *, char *const []) = execvp;
  void         (*au)(int) = _exit;
  int          (*av)(int, uid_t, gid_t) = fchown;
  int          (*aw)(int) = fchdir;
  int          (*ax)(int) = fdatasync;
  pid_t        (*ay)(void) = fork;
  long         (*az)(int, int) = fpathconf;
  int          (*ba)(int) = fsync;
  int          (*bb)(int, off_t) = ftruncate;
  char        *(*bc)(char *, size_t) = getcwd;
/*int          (*bd)(void) = getdtablesize; (LEGACY) */
  gid_t        (*be)(void) = getegid;
  uid_t        (*bf)(void) = geteuid;
  gid_t        (*bg)(void) = getgid;
  int          (*bh)(int, gid_t []) = getgroups;
  long         (*bi)(void) = gethostid;
  char        *(*bj)(void) = getlogin;
  int          (*bk)(char *, size_t) = getlogin_r;
  int          (*bl)(int, char * const [], const char *) = getopt;
/*int          (*bm)(void) = getpagesize; (LEGACY) */
/*char        *(*bn)(const char *) = getpass; (LEGACY) */
  pid_t        (*bo)(pid_t) = getpgid;
  pid_t        (*bp)(void) = getpgrp;
  pid_t        (*bq)(void) = getpid;
  pid_t        (*br)(void) = getppid;
  pid_t        (*bs)(pid_t) = getsid;
  uid_t        (*bt)(void) = getuid;
  char        *(*bu)(char *) = getwd;
  int          (*bv)(int) = isatty;
  int          (*bw)(const char *, uid_t, gid_t) = lchown;
  int          (*bx)(const char *, const char *) = link;
  int          (*by)(int, int, off_t) = lockf;
  off_t        (*bz)(int, off_t, int) = lseek;
  int          (*ca)(int) = nice;
  long         (*cb)(const char *, int) = pathconf;
  int          (*cc)(void) = pause;
  int          (*cd)(int [2]) = pipe;
  ssize_t      (*ce)(int, void *, size_t, off_t) = pread;
  ssize_t      (*cg)(int, const void *, size_t, off_t) = pwrite;
  ssize_t      (*ch)(int, void *, size_t) = read;
  ssize_t      (*ci)(const char *, char *, size_t) = readlink;
  int          (*cj)(const char *) = rmdir;
  void        *(*ck)(intptr_t) = sbrk;
  int          (*cl)(gid_t) = setgid;
  int          (*cm)(pid_t, pid_t) = setpgid;
  pid_t        (*cn)(void) = setpgrp;
  int          (*co)(gid_t, gid_t) = setregid;
  int          (*cp)(uid_t, uid_t) = setreuid;
  pid_t        (*cq)(void) = setsid;
  int          (*cr)(uid_t) = setuid;
  unsigned     (*cs)(unsigned) = sleep;
  void         (*ct)(const void *, void *, ssize_t) = swab;
  int          (*cu)(const char *, const char *) = symlink;
  void         (*cv)(void) = sync;
  long         (*cw)(int) = sysconf;
  pid_t        (*cx)(int) = tcgetpgrp;
  int          (*cy)(int, pid_t) = tcsetpgrp;
  int          (*cz)(const char *, off_t) = truncate;
  char        *(*da)(int) = ttyname;
  int          (*db)(int, char *, size_t) = ttyname_r;
  useconds_t   (*dc)(useconds_t, useconds_t) = ualarm;
  int          (*dd)(const char *) = unlink;
  int          (*de)(useconds_t) = usleep;
  pid_t        (*df)(void) = vfork;
  ssize_t      (*dg)(int, const void *, size_t) = write;
}
