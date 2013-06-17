#include <iso646.h>

void f(int a, int b, int c)
{
  int d = (a and b);
  int e = (a bitand b);
  int f = (a bitor b);
  int g = (compl b);
  int h = (not b);
  int i = (a or b);
  int j = (a xor b);
  int k = (a not_eq b);

  e and_eq c;
  f or_eq c;
  j xor_eq c;
}
