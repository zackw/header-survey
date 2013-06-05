/* baseline */
#include <stddef.h>

struct x
{
  int a;
  double b;
};

void fn(void)
{
  ptrdiff_t p;
  size_t s;
  wchar_t w;
  struct x *xx = NULL;
  size_t o = offsetof(struct x, b);
}
