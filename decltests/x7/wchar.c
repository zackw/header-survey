/* features */
#include <wchar.h>

void f(void)
{
  FILE *(*a)(wchar_t **, size_t *) = open_wmemstream;

  size_t (*b)(wchar_t *, const char **, size_t, size_t, mbstate_t *)
    = mbsnrtowcs;
  size_t (*c)(char *, const wchar_t **, size_t, size_t, mbstate_t *)
    = wcsnrtombs;

  wchar_t *(*d)(wchar_t *, const wchar_t *) = wcpcpy;
  wchar_t *(*e)(wchar_t *, const wchar_t *, size_t) = wcpncpy;
  wchar_t *(*f)(const wchar_t *) = wcsdup;
  size_t   (*g)(const wchar_t *, size_t) = wcsnlen;

  int    (*h)(const wchar_t *, const wchar_t *, locale_t) = wcscoll_l;
  size_t (*i)(wchar_t *, const wchar_t *, size_t, locale_t) = wcsxfrm_l;

  int (*j)(const wchar_t *, const wchar_t *) = wcscasecmp;
  int (*k)(const wchar_t *, const wchar_t *, locale_t) = wcscasecmp_l;
  int (*l)(const wchar_t *, const wchar_t *, size_t) = wcsncasecmp;
  int (*m)(const wchar_t *, const wchar_t *, size_t, locale_t) = wcsncasecmp_l;
}
