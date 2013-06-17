#include <string.h>

void f(char *a, size_t c)
{
  char *b = NULL;

  void *d = memcpy(b, a, c);
  void *e = memmove(a, b, c);
  char *f = strcpy(b, a);
  char *g = strncpy(a, b, c);
  char *h = strcat(a, b);
  char *i = strncat(a, b, c);

  int j = memcmp(a, b, c);
  int k = strcmp(a, b);
  int l = strcoll(a, b);
  int n = strncmp(a, b, c);
  size_t o = strxfrm(a, b, c);

  void *p = memchr(a, 'a', c);
  char *q = strchr(a, 'a');
  size_t r = strcspn(a, "ab");
  char *s = strpbrk(a, ":;");
  char *t = strrchr(a, 'z');
  size_t u = strspn(a, " \t");
  char *v = strstr(a, "word");
  char *w = strtok(a, ":;");
  void *x = memset(b, ' ', 33);
  char *y = strerror(1);
  size_t z = strlen(a);
}
