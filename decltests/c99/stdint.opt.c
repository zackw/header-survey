/* optional: fixed-width types */
#ifndef NO_INCLUDE_STDINT_H /* see inttypes-c99-o.c */
#include <stdint.h>
#endif

/* exact-width integer types; we only check 8/16/32/64 */
void ewi(void)
{
  int8_t a;
  uint8_t au;
  int16_t b;
  uint16_t bu;
  int32_t c;
  uint32_t cu;
  int64_t d;
  uint64_t du;
}

#if INT8_MIN != INT8_C(-128)
#error "INT8_MIN"
#endif
#if INT8_MAX != INT8_C(127)
#error "INT8_MAX"
#endif
#if UINT8_MAX != UINT8_C(255)
#error "UINT8_MAX"
#endif

#if INT16_MIN != INT16_C(-32768)
#error "INT16_MIN"
#endif
#if INT16_MAX != INT16_C(32767)
#error "INT16_MAX"
#endif
#if UINT16_MAX != UINT16_C(65535)
#error "UINT16_MAX"
#endif

#if INT32_MIN != INT32_C(-2147483648)
#error "INT32_MIN"
#endif
#if INT32_MAX != INT32_C(2147483647)
#error "INT32_MAX"
#endif
#if UINT32_MAX != UINT32_C(4294967295)
#error "UINT32_MAX"
#endif

#if INT64_MIN != INT64_C(-9223372036854775807) - 1
#error "INT64_MIN"
#endif
#if INT64_MAX != INT64_C(9223372036854775807)
#error "INT64_MAX"
#endif
#if UINT64_MAX != UINT64_C(18446744073709551615)
#error "UINT64_MAX"
#endif

/* pointer-holding types */
void ph(void)
{
  intptr_t p;
  uintptr_t pu;
}

#if INTPTR_MIN > -32767
#error "INTPTR_MIN"
#endif
#if INTPTR_MAX <  32767
#error "INTPTR_MIN"
#endif
#if UINTPTR_MAX < 65535
#error "UINTPTR_MAX"
#endif
