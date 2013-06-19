/* functions */
#include <wctype.h>

void f(void)
{
  int       (*a)(wint_t, locale_t) = iswalnum_l;
  int       (*b)(wint_t, locale_t) = iswalpha_l;
  int       (*c)(wint_t, locale_t) = iswblank_l;
  int       (*d)(wint_t, locale_t) = iswcntrl_l;
  int       (*e)(wint_t, locale_t) = iswdigit_l;
  int       (*f)(wint_t, locale_t) = iswgraph_l;
  int       (*g)(wint_t, locale_t) = iswlower_l;
  int       (*h)(wint_t, locale_t) = iswprint_l;
  int       (*i)(wint_t, locale_t) = iswpunct_l;
  int       (*j)(wint_t, locale_t) = iswspace_l;
  int       (*k)(wint_t, locale_t) = iswupper_l;
  int       (*l)(wint_t, locale_t) = iswxdigit_l;
  wint_t    (*m)(wint_t, locale_t) = towlower_l;
  wint_t    (*n)(wint_t, locale_t) = towupper_l;
  wctype_t  (*o)(const char *, locale_t) = wctype_l;
  int       (*p)(wint_t, wctype_t, locale_t) = iswctype_l;
  wctrans_t (*q)(const char *, locale_t) = wctrans_l;
  wint_t    (*r)(wint_t, wctrans_t, locale_t) = towctrans_l;
}
