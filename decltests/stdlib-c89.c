/* baseline */
#include <stdlib.h>

void tm(void)
{
  size_t a;
  wchar_t b;
  div_t c;
  ldiv_t d;
  long int *e = NULL;
  int f = RAND_MAX;
  int g = MB_CUR_MAX;

  c.quot = 0;
  c.rem  = 12;
  d.quot = 45;
  d.rem  = 78;
}

extern int A, B, C;

void cleanup(void)
{
}

int compar(const void *a, const void *b)
{
  int aa = *(const int *)a;
  int bb = *(const int *)b;
  return bb - aa;
}

void fn(void)
{
  double a = atof("1.23");
  int    b = atoi("123");
  long   c = atol("123456789");
  char *endp;
  double d = strtod("1.23cheese", &endp);
  long   e = strtol("0x1243", &endp, 0);
  unsigned long f = strtoul("12aelt", &endp, 36);

  int g = rand();

  void *h = calloc(12, 44);
  void *i = malloc(12 * 44);
  void *j = realloc(i, 12 * 77);

  int k = atexit(cleanup);

  char *l = getenv("PATH");
  int m = system(NULL);

  int n[24];
  int o = 99;
  int *p = bsearch(&o, n, 24, sizeof(int), compar);

  int q = abs(-9999);
  div_t r = div(1435, 12);
  long s = labs(-999999999L);
  ldiv_t t = ldiv(14123415L, 12);

  wchar_t w[4];
  char x[4];
  int u = mblen("\xe2\x80\x94", 3);
  int v = mbtowc(w, "\xe2\x80\x94", 3);
  int y = wctomb(x, w[0]);

  v = mbstowcs(w, "\xe2\x80\x94", 4);
  y = wcstombs(x, w, 4);

  /* these are last because they return no value */
  qsort(n, 24, sizeof(int), compar);
  srand(99999);
  free(h);

  /* these are conditional because the compiler might be aware that they
     don't return */
  if (A) abort();
  if (B) exit(EXIT_SUCCESS);
  if (C) exit(EXIT_FAILURE);
}
