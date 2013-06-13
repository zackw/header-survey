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
  int j = isspace(c);
  int k = isupper(c);
  int l = isxdigit(c);
  int m = tolower(c);
  int n = toupper(c);
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
  int j = (isspace)(c);
  int k = (isupper)(c);
  int l = (isxdigit)(c);
  int m = (tolower)(c);
  int n = (toupper)(c);
}
