#include <libgen.h>

char *(*a)(char *) = basename;
char *(*b)(char *) = dirname;

/* __loc1, regcmp, regex obsolete in Issue 5, removed in 6 */
