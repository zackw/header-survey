/* C99 additions */
#include <wctype.h>

/* note: C89/C99 distinction for this header deduced by comparing SUSv2 to C99,
   as I don't have an official copy of C89.  May not be 100% accurate. */

void f(wint_t a)
{
  int b = iswblank(a);
}
