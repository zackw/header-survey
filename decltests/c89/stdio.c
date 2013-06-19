#include <stdio.h>

/* L_tmpnam, tmpnam, TMP_MAX excluded: obsolescent in Issue 7, unsafe
   gets excluded: removed in C2011, unsafe */

void tm(void)
{
  FILE *a = stderr;
  FILE *b = stdin;
  FILE *c = stdout;

  size_t d = FOPEN_MAX;
  size_t e = FILENAME_MAX;

  fpos_t f;

  char *g = NULL;
  int   h = EOF;
}

void fn(void)
{
  int a   = remove("file");
  int b   = rename("old", "new");
  FILE *c = tmpfile();

  char d[BUFSIZ];
  char *e;

  int f = fclose(c);
  int g = fflush(c);

  FILE *h = fopen("file", "r");
  FILE *i = freopen("file", "r", stdin);

  char j[BUFSIZ];
  setbuf(i, j);

  a = setvbuf(h, j, _IOFBF, BUFSIZ);
  a = setvbuf(h, j, _IOLBF, BUFSIZ);
  a = setvbuf(h, NULL, _IONBF, 0);

  a = fprintf(h, "%s\n", "text");
  a = fscanf(h, "%s\n", j);
  a = printf("%s\n", "text");
  a = scanf("%s\n", j);
  a = sprintf(j, "%s\n", "text");
  a = sscanf(j, "%s\n", d);

  a = fgetc(h);
  e = fgets(j, BUFSIZ, h);
  a = fputc('x', h);
  a = fputs("text", h);

  a = getc(h);
  a = getchar();

  a = putc('x', h);
  a = putchar('x');
  a = puts("text");
  a = ungetc('x', h);
}

void fn2(FILE *a)
{
  char b[BUFSIZ];
  size_t n = fread(b, 1, BUFSIZ, a);
  size_t m = fwrite(b, 1, BUFSIZ, a);

  fpos_t pos;
  int c = fgetpos(a, &pos);
  int d = fsetpos(a, &pos);

  int e = fseek(a, 0, SEEK_SET);
  int f = fseek(a, 1024*1024*1024L, SEEK_CUR);
  int g = fseek(a, -1024, SEEK_END);

  long h = ftell(a);

  int i = feof(a);
  int j = ferror(a);

  clearerr(a);
  rewind(a);
  perror("aye");
}

#include <stdarg.h>

void vfn(const char *m, ...)
{
  va_list ap;
  int a;
  char b[BUFSIZ];
  va_start(ap, m);
  a = vfprintf(stderr, m, ap);
  a = vprintf(m, ap);
  a = vsprintf(b, m, ap);
  va_end(ap);
}
