#include <wctype.h>

/* note: C89/C99 distinction for this header deduced by comparing SUSv2 to C99,
   as I don't have an official copy of C89.  May not be 100% accurate. */

void f(wint_t a)
{
  wint_t b = WEOF;
  wctrans_t c = wctrans("eka");
  wctype_t d = wctype("dvi");

  int e = iswalnum(a);
  int f = iswalpha(a);
  int g = iswcntrl(a);
  int h = iswdigit(a);
  int i = iswgraph(a);
  int j = iswlower(a);
  int k = iswprint(a);
  int l = iswpunct(a);
  int m = iswspace(a);
  int n = iswupper(a);
  int o = iswxdigit(a);
  int p = iswctype(a, d);

  wint_t q = towlower(a);
  wint_t r = towupper(a);
  wint_t s = towctrans(a, c);
}

