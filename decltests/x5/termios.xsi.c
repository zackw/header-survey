/* XSI: features */
#include <termios.h>

tcflag_t iflags[] = {
  IXANY,
};

tcflag_t oflags[] = {
  ONLCR,
  OCRNL,
  ONOCR,
  ONLRET,
  OFILL,
  NLDLY,
  NL0,
  NL1,
  CRDLY,
  CR0,
  CR1,
  CR2,
  CR3,
  TABDLY,
  TAB0,
  TAB1,
  TAB2,
  TAB3,
  BSDLY,
  BS0,
  BS1,
  VTDLY,
  VT0,
  VT1,
  FFDLY,
  FF0,
  FF1,
};

void f(int cc)
{
  pid_t   i = tcgetsid(cc);
}
