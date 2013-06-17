#include <regex.h>

int f(void)
{
  regex_t aa;
  size_t *aan = &aa.re_nsub;
  regmatch_t bb;
  regoff_t *bbs = &bb.rm_so;
  regoff_t *bbe = &bb.rm_eo;

  int a = regcomp(&aa, "bla.*h", REG_EXTENDED|REG_ICASE|REG_NOSUB|REG_NEWLINE);
  int b = regexec(&aa, "xblagrt", (size_t)1, &bb, REG_NOTBOL|REG_NOTEOL);

  char errbuf[256];
  size_t c = regerror(b, &aa, errbuf, sizeof errbuf);

  regfree(&aa);

  switch (a) {
  case REG_NOMATCH:
  case REG_BADPAT:
  case REG_ECOLLATE:
  case REG_ECTYPE:
  case REG_EESCAPE:
  case REG_ESUBREG:
  case REG_EBRACK:
  case REG_ENOSYS:
  case REG_EPAREN:
  case REG_EBRACE:
  case REG_BADBR:
  case REG_ERANGE:
  case REG_ESPACE:
  case REG_BADRPT:
    return 1;
  default:
    return 0;
  }
}
