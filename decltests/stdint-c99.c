/* baseline */
#ifndef NO_INCLUDE_STDINT_H /* see inttypes-c99.c */
#include <stdint.h>
#endif

/* required minimum-width integer types */
void mwi(void)
{
  int_least8_t a;
  uint_least8_t au;
  int_least16_t b;
  uint_least16_t bu;
  int_least32_t c;
  uint_least32_t cu;
  int_least64_t d;
  uint_least64_t du;
}

#if INT_LEAST8_MIN > INT8_C(-127)
#error "INT_LEAST8_MIN"
#endif
#if INT_LEAST8_MAX < INT8_C(127)
#error "INT_LEAST8_MAX"
#endif
#if UINT_LEAST8_MAX < UINT8_C(255)
#error "UINT_LEAST8_MAX"
#endif

#if INT_LEAST16_MIN > INT16_C(-32767)
#error "INT_LEAST16_MIN"
#endif
#if INT_LEAST16_MAX < INT16_C(32767)
#error "INT_LEAST16_MAX"
#endif
#if UINT_LEAST16_MAX < UINT16_C(65535)
#error "UINT_LEAST16_MAX"
#endif

#if INT_LEAST32_MIN > INT32_C(-2147483647)
#error "INT_LEAST32_MIN"
#endif
#if INT_LEAST32_MAX < INT32_C(2147483647)
#error "INT_LEAST32_MAX"
#endif
#if UINT_LEAST32_MAX < UINT32_C(4294967295)
#error "UINT_LEAST32_MAX"
#endif

#if INT_LEAST64_MIN > INT64_C(-9223372036854775807)
#error "INT_LEAST64_MIN"
#endif
#if INT_LEAST64_MAX < INT64_C(9223372036854775807)
#error "INT_LEAST64_MAX"
#endif
#if UINT_LEAST64_MAX < UINT64_C(18446744073709551615)
#error "UINT_LEAST64_MAX"
#endif

/* required fastest integer types */
void fwi(void)
{
  int_fast8_t a;
  uint_fast8_t au;
  int_fast16_t b;
  uint_fast16_t bu;
  int_fast32_t c;
  uint_fast32_t cu;
  int_fast64_t d;
  uint_fast64_t du;
}

#if INT_FAST8_MIN > INT8_C(-127)
#error "INT_FAST8_MIN"
#endif
#if INT_FAST8_MAX < INT8_C(127)
#error "INT_FAST8_MAX"
#endif
#if UINT_FAST8_MAX < UINT8_C(255)
#error "UINT_FAST8_MAX"
#endif

#if INT_FAST16_MIN > INT16_C(-32767)
#error "INT_FAST16_MIN"
#endif
#if INT_FAST16_MAX < INT16_C(32767)
#error "INT_FAST16_MAX"
#endif
#if UINT_FAST16_MAX < UINT16_C(65535)
#error "UINT_FAST16_MAX"
#endif

#if INT_FAST32_MIN > INT32_C(-2147483647)
#error "INT_FAST32_MIN"
#endif
#if INT_FAST32_MAX < INT32_C(2147483647)
#error "INT_FAST32_MAX"
#endif
#if UINT_FAST32_MAX < UINT32_C(4294967295)
#error "UINT_FAST32_MAX"
#endif

#if INT_FAST64_MIN > INT64_C(-9223372036854775807)
#error "INT_FAST64_MIN"
#endif
#if INT_FAST64_MAX < INT64_C(9223372036854775807)
#error "INT_FAST64_MAX"
#endif
#if UINT_FAST64_MAX < UINT64_C(18446744073709551615)
#error "UINT_FAST64_MAX"
#endif

/* maximum-width types */
void maxi(void)
{
  intmax_t m;
  uintmax_t mu;
}

#if INTMAX_MIN > INTMAX_C(-9223372036854775807)
#error "INTMAX_MIN"
#endif
#if INTMAX_MAX < INTMAX_C(9223372036854775807)
#error "INTMAX_MIN"
#endif
#if UINTMAX_MAX < UINTMAX_C(18446744073709551615)
#error "UINTMAX_MAX"
#endif

/* other required limit macros */
#if PTRDIFF_MIN > -65535
#error "PTRDIFF_MIN"
#endif
#if PTRDIFF_MAX <  65535
#error "PTRDIFF_MAX"
#endif

#if SIZE_MAX < 65535
#error "SIZE_MAX"
#endif

#if SIG_ATOMIC_MIN == 0
# if SIG_ATOMIC_MAX < 255
#  error "SIG_ATOMIC_MAX (unsigned)"
# endif
#else
# if SIG_ATOMIC_MIN > -127
#  error "SIG_ATOMIC_MIN (signed)"
# endif
# if SIG_ATOMIC_MAX < 127
#  error "SIG_ATOMIC_MAX (signed)"
# endif
#endif

#if WCHAR_MIN == 0
# if WCHAR_MAX < 255
#  error "WCHAR_MAX (unsigned)"
# endif
#else
# if WCHAR_MIN > -127
#  error "WCHAR_MIN (signed)"
# endif
# if WCHAR_MAX < 127
#  error "WCHAR_MAX (signed)"
# endif
#endif

#if WINT_MIN == 0
# if WINT_MAX < 65535
#  error "WINT_MAX (unsigned)"
# endif
#else
# if WINT_MIN > -32767
#  error "WINT_MIN (signed)"
# endif
# if WINT_MAX < 32767
#  error "WINT_MAX (signed)"
# endif
#endif
