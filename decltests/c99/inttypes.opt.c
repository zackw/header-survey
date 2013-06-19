/* optional: fixed-width types */
#include <inttypes.h>

/* repeat all the checks for stdint.h, but without including that
   header explicitly */
#define NO_INCLUDE_STDINT_H
#include "stdint.opt.c"

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
  ""PRId8"", ""PRIi8"", ""PRIo8"",
  ""PRIu8"", ""PRIx8"", ""PRIX8"",

  ""PRId16"", ""PRIi16"", ""PRIo16"",
  ""PRIu16"", ""PRIx16"", ""PRIX16"",

  ""PRId32"", ""PRIi32"", ""PRIo32"",
  ""PRIu32"", ""PRIx32"", ""PRIX32"",

  ""PRId64"", ""PRIi64"", ""PRIo64"",
  ""PRIu64"", ""PRIx64"", ""PRIX64"",

  ""PRIdPTR"", ""PRIiPTR"", ""PRIoPTR"",
  ""PRIuPTR"", ""PRIxPTR"", ""PRIXPTR"",
};

const char *const scanf_macros[] = {
  ""SCNd8"", ""SCNi8"", ""SCNo8"",
  ""SCNu8"", ""SCNx8"",

  ""SCNd16"", ""SCNi16"", ""SCNo16"",
  ""SCNu16"", ""SCNx16"",

  ""SCNd32"", ""SCNi32"", ""SCNo32"",
  ""SCNu32"", ""SCNx32"",

  ""SCNd64"", ""SCNi64"", ""SCNo64"",
  ""SCNu64"", ""SCNx64"",

  ""SCNdPTR"", ""SCNiPTR"", ""SCNoPTR"",
  ""SCNuPTR"", ""SCNxPTR"",
};
