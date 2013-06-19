/* XSI: features */
#include <grp.h>

struct group *(*a)(void) = getgrent;
void          (*b)(void) = endgrent;
void          (*c)(void) = setgrent;
