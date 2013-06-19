#include <spawn.h>

short xx[] = {
  POSIX_SPAWN_RESETIDS,
  POSIX_SPAWN_SETPGROUP,
  POSIX_SPAWN_SETSIGDEF,
  POSIX_SPAWN_SETSIGMASK,
};

void t(void)
{
  posix_spawnattr_t spa;
  posix_spawn_file_actions_t spf;
  /* technically the next three are only required in Issue 7, but it is
     unlikely that anyone didn't */
  mode_t m;
  pid_t p;
  sigset_t ss;
}

void f(void)
{
  int (*a)(pid_t *, const char *, const posix_spawn_file_actions_t *,
           const posix_spawnattr_t *, char *const [], char *const [])
    = posix_spawn;
  int (*b)(posix_spawn_file_actions_t *, int)
    = posix_spawn_file_actions_addclose;
  int (*c)(posix_spawn_file_actions_t *, int, int)
    = posix_spawn_file_actions_adddup2;
  int (*d)(posix_spawn_file_actions_t *, int, const char *, int, mode_t)
    = posix_spawn_file_actions_addopen;
  int (*e)(posix_spawn_file_actions_t *) = posix_spawn_file_actions_destroy;
  int (*f)(posix_spawn_file_actions_t *) = posix_spawn_file_actions_init;
  int (*g)(posix_spawnattr_t *) = posix_spawnattr_destroy;
  int (*h)(const posix_spawnattr_t *, sigset_t *)
    = posix_spawnattr_getsigdefault;
  int (*i)(const posix_spawnattr_t *, short *) = posix_spawnattr_getflags;
  int (*j)(const posix_spawnattr_t *, pid_t *) = posix_spawnattr_getpgroup;
  int (*k)(const posix_spawnattr_t *, sigset_t *)
    = posix_spawnattr_getsigmask;
  int (*l)(posix_spawnattr_t *) = posix_spawnattr_init;
  int (*m)(posix_spawnattr_t *, const sigset_t *)
    = posix_spawnattr_setsigdefault;
  int (*n)(posix_spawnattr_t *, short) = posix_spawnattr_setflags;
  int (*o)(posix_spawnattr_t *, pid_t) = posix_spawnattr_setpgroup;
  int (*p)(posix_spawnattr_t *, const sigset_t *)
    = posix_spawnattr_setsigmask;
  int (*q)(pid_t *, const char *, const posix_spawn_file_actions_t *,
           const posix_spawnattr_t *, char *const [], char *const [])
    = posix_spawnp;
}
