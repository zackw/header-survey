/* baseline */
#include <inttypes.h>

/* repeat all the checks for stdint.h, but without including that
   header explicitly */
#define NO_INCLUDE_STDINT_H
#include "stdint-c99.c"

/* There is no way to validate the *contents* of the PRI* and SCN*
   macros in a compile test, so we just make sure they're there, and
   do in fact expand to string literals, for all the mandatory types.
   We do not permit the implementation to take advantage of the
   "unless the implementation does not have a suitable fscanf length
   modifier for the type" qualification, because I don't see any
   excuse for that, do you?  */

/* The leading and trailing "" are how we check that the macro
   actually expands to a string literal; if it is, string literal
   concatenation will happen, otherwise it'll be a syntax error.  */
const char *const printf_macros[] = {
  ""PRIdLEAST8"", ""PRIiLEAST8"", ""PRIoLEAST8"",
  ""PRIuLEAST8"", ""PRIxLEAST8"", ""PRIXLEAST8"",

  ""PRIdLEAST16"", ""PRIiLEAST16"", ""PRIoLEAST16"",
  ""PRIuLEAST16"", ""PRIxLEAST16"", ""PRIXLEAST16"",

  ""PRIdLEAST32"", ""PRIiLEAST32"", ""PRIoLEAST32"",
  ""PRIuLEAST32"", ""PRIxLEAST32"", ""PRIXLEAST32"",

  ""PRIdLEAST64"", ""PRIiLEAST64"", ""PRIoLEAST64"",
  ""PRIuLEAST64"", ""PRIxLEAST64"", ""PRIXLEAST64"",

  ""PRIdFAST8"", ""PRIiFAST8"", ""PRIoFAST8"",
  ""PRIuFAST8"", ""PRIxFAST8"", ""PRIXFAST8"",

  ""PRIdFAST16"", ""PRIiFAST16"", ""PRIoFAST16"",
  ""PRIuFAST16"", ""PRIxFAST16"", ""PRIXFAST16"",

  ""PRIdFAST32"", ""PRIiFAST32"", ""PRIoFAST32"",
  ""PRIuFAST32"", ""PRIxFAST32"", ""PRIXFAST32"",

  ""PRIdFAST64"", ""PRIiFAST64"", ""PRIoFAST64"",
  ""PRIuFAST64"", ""PRIxFAST64"", ""PRIXFAST64"",

  ""PRIdMAX"", ""PRIiMAX"", ""PRIoMAX"",
  ""PRIuMAX"", ""PRIxMAX"", ""PRIXMAX"",
};

const char *const scanf_macros[] = {
  ""SCNdLEAST8"", ""SCNiLEAST8"", ""SCNoLEAST8"",
  ""SCNuLEAST8"", ""SCNxLEAST8"",

  ""SCNdLEAST16"", ""SCNiLEAST16"", ""SCNoLEAST16"",
  ""SCNuLEAST16"", ""SCNxLEAST16"",

  ""SCNdLEAST32"", ""SCNiLEAST32"", ""SCNoLEAST32"",
  ""SCNuLEAST32"", ""SCNxLEAST32"",

  ""SCNdLEAST64"", ""SCNiLEAST64"", ""SCNoLEAST64"",
  ""SCNuLEAST64"", ""SCNxLEAST64"",

  ""SCNdFAST8"", ""SCNiFAST8"", ""SCNoFAST8"",
  ""SCNuFAST8"", ""SCNxFAST8"",

  ""SCNdFAST16"", ""SCNiFAST16"", ""SCNoFAST16"",
  ""SCNuFAST16"", ""SCNxFAST16"",

  ""SCNdFAST32"", ""SCNiFAST32"", ""SCNoFAST32"",
  ""SCNuFAST32"", ""SCNxFAST32"",

  ""SCNdFAST64"", ""SCNiFAST64"", ""SCNoFAST64"",
  ""SCNuFAST64"", ""SCNxFAST64"",

  ""SCNdMAX"", ""SCNiMAX"", ""SCNoMAX"",
  ""SCNuMAX"", ""SCNxMAX"",
};


/* "Functions for greatest-width integer types" */
void f(intmax_t aa, intmax_t bb, char *s)
{
  intmax_t a  = imaxabs(aa);
  imaxdiv_t b = imaxdiv(aa, bb);
  intmax_t *c = &b.quot;
  intmax_t *d = &b.rem;

  char *ss;
  intmax_t  e = strtoimax(s, &ss, 0);
  uintmax_t f = strtoumax(s, &ss, 0);
}

#include <stddef.h>
void g(wchar_t *w)
{
  wchar_t *ww;
  intmax_t a  = wcstoimax(w, &ww, 0);
  uintmax_t b = wcstoumax(w, &ww, 0);
}
