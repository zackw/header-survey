/* baseline */
#include <ctype.h>

void fn(int c)
{
  int a = isalnum(c);
  int b = isalpha(c);
  int d = iscntrl(c);
  int e = isdigit(c);
  int f = isgraph(c);
  int g = islower(c);
  int h = isprint(c);
  int i = ispunct(c);
  int j = isupper(c);
  int k = isxdigit(c);
  int l = tolower(c);
  int m = toupper(c);
}

/* some pre-standard C libraries only provided these as macros;
   C1989 requires them to be (additionally) functions. */
void fn2(int c)
{
  int a = (isalnum)(c);
  int b = (isalpha)(c);
  int d = (iscntrl)(c);
  int e = (isdigit)(c);
  int f = (isgraph)(c);
  int g = (islower)(c);
  int h = (isprint)(c);
  int i = (ispunct)(c);
  int j = (isupper)(c);
  int k = (isxdigit)(c);
  int l = (tolower)(c);
  int m = (toupper)(c);
}
