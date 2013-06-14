/* baseline */
#include <libgen.h>

void f(char *aa)
{
  char *a = basename(aa);
  char *b = dirname(aa);
}

#if 0
/* These declarations were already tagged obsolete in X5. */
void l(void)
{
  char **a = &__loc1;

  char *b = regcmp("word", "(word)$1", "word", (char *)0);
  char *c;
  char *d = regex(b, "wordwordword", &c);
}
#endif
