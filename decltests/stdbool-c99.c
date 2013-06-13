/* baseline */
#include <stdbool.h>

#if !defined true || true != 1
#error "true"
#endif
#if !defined false || false != 0
#error "false"
#endif
#if !defined __bool_true_false_are_defined || __bool_true_false_are_defined != 1
#error "__bool_true_false_are_defined"
#endif

void f(bool x)
{
  x = true;
  x = false;
}
