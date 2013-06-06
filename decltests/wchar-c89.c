/* baseline */
#include <wchar.h>

/* note: C89/C99 distinction for this header deduced by comparing
   SUSv2 to C99, as I don't have an official copy of C89.  May not be
   100% accurate.  SUSv2 requires a bunch of the <wctype.h> decls to
   appear also in <wchar.h>, but C99 doesn't, so I am assuming C89
   didn't either. */

void c(void)
{
  wchar_t a = WCHAR_MAX;
  wchar_t b = WCHAR_MIN;
  wint_t  c = WEOF;
  char   *d = NULL;
}

void f(FILE *ff, int bb, wint_t cc, wchar_t dd,
       const char *rr,
       const wchar_t *ss, const wchar_t *tt,
       wchar_t *uu, char *vv, size_t nn,
       const struct tm *tm)
{
  mbstate_t mbs;
  wchar_t **uup = &uu;
  const wchar_t **ssp = &ss;
  const char **rrp = &rr;
  int ii, jj, kk;

  wint_t   a  = btowc(bb);
  int      b  = fwprintf(ff, ss, 1, 2, 3);
  int      c  = fwscanf(ff, ss, &ii, &jj, &kk);
  wint_t   d  = fgetwc(ff);
  wchar_t *e  = fgetws(uu, bb, ff);
  wint_t   f  = fputwc(dd, ff);
  int      g  = fputws(ss, ff);
  int      h  = fwide(ff, 0);
  wint_t   i  = getwc(ff);
  wint_t   j  = getwchar();
  int      k  = mbsinit(&mbs);
  size_t   l  = mbrlen(rr, nn, &mbs);
  size_t   m  = mbrtowc(uu, rr, nn, &mbs);
  size_t   n  = mbsrtowcs(uu, rrp, nn, &mbs);
  wint_t   o  = putwc(dd, ff);
  wint_t   p  = putwchar(dd);
  int      q  = swprintf(uu, nn, ss, 1, 2, 3);
  int      r  = swscanf(ss, tt, &ii, &jj, &kk);
  wint_t   s  = ungetwc(cc, ff);
  size_t   t  = wcrtomb(vv, dd, &mbs);
  wchar_t *u  = wcscat(uu, ss);
  wchar_t *v  = wcschr(ss, dd);
  int      w  = wcscmp(ss, tt);
  int      x  = wcscoll(ss, tt);
  wchar_t *y  = wcscpy(uu, ss);
  size_t   z  = wcscspn(ss, tt);
  size_t   ab = wcsftime(uu, nn, ss, tm);
  size_t   ac = wcslen(ss);
  wchar_t *ad = wcsncat(uu, ss, nn);
  int      ae = wcsncmp(ss, tt, nn);
  wchar_t *af = wcsncpy(uu, ss, nn);
  wchar_t *ag = wcspbrk(ss, tt);
  wchar_t *ah = wcsrchr(ss, dd);
  size_t   ai = wcsrtombs(vv, ssp, nn, &mbs);
  size_t   aj = wcsspn(ss, tt);
  wchar_t *ak = wcsstr(ss, tt);
  double   al = wcstod(ss, uup);
  wchar_t *am = wcstok(uu, ss, uup);
  long     an = wcstol(ss, uup, 10);
  unsigned long ao = wcstoul(ss, uup, 10);
  size_t   ap = wcsxfrm(uu, ss, nn);
  int      aq = wctob(cc);
  wchar_t *ar = wmemchr(ss, dd, nn);
  int      as = wmemcmp(ss, tt, nn);
  wchar_t *at = wmemcpy(uu, ss, nn);
  wchar_t *au = wmemmove(uu, ss, nn);
  wchar_t *av = wmemset(uu, dd, nn);
  int      aw = wprintf(ss, 1, 2, 3);
  int      ax = wscanf(ss, &ii, &jj, &kk);
}

#include <stdarg.h>

void vf(FILE *ff, const wchar_t *ss, wchar_t *uu, size_t nn, ...)
{
  va_list ap;
  va_start(ap, nn);

  int a = vfwprintf(ff, ss, ap);
  int b = vwprintf(ss, ap);
  int c = vswprintf(uu, nn, ss, ap);

  va_end(ap);
}
