/* explicit-locale character classification functions */
#include <ctype.h>

/* isascii, toascii, _toupper, _tolower are obsolete, so excluded */

void f(int aa, locale_t bb)
{
  int
    a = isalnum_l(aa, bb),
    b = isalpha_l(aa, bb),
    c = isblank_l(aa, bb),
    d = iscntrl_l(aa, bb),
    e = isdigit_l(aa, bb),
    f = isgraph_l(aa, bb),
    g = islower_l(aa, bb),
    h = isprint_l(aa, bb),
    i = ispunct_l(aa, bb),
    j = isspace_l(aa, bb),
    k = isupper_l(aa, bb),
    l = isxdigit_l(aa, bb),
    m = toupper_l(aa, bb),
    n = tolower_l(aa, bb);
}
