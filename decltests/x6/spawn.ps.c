/* optional: scheduling controls */
#include <spawn.h>

short xx[] = {
  POSIX_SPAWN_SETSCHEDPARAM,
  POSIX_SPAWN_SETSCHEDULER,
};

void f(void)
{
  int (*a)(const posix_spawnattr_t *, struct sched_param *)
    = posix_spawnattr_getschedparam;
  int (*b)(const posix_spawnattr_t *, int *) = posix_spawnattr_getschedpolicy;
  int (*c)(posix_spawnattr_t *, const struct sched_param *)
    = posix_spawnattr_setschedparam;
  int (*d)(posix_spawnattr_t *, int) = posix_spawnattr_setschedpolicy;
}
