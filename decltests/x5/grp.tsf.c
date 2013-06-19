/* thread-safe functions */
#include <grp.h>

int (*a)(gid_t, struct group *, char *, size_t, struct group **) = getgrgid_r;
int (*b)(const char *, struct group *, char *, size_t, struct group **) = getgrnam_r;
