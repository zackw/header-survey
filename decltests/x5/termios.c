#include <termios.h>

/* LEGACY in Issue 5, removed in 6:
   IUCLC, OLCUC, XCASE */

void t(void)
{
  struct termios c;
  tcflag_t *ci = &c.c_iflag;
  tcflag_t *co = &c.c_oflag;
  tcflag_t *cc = &c.c_cflag;
  tcflag_t *cl = &c.c_lflag;
  cc_t     *cC =  c.c_cc;
}

unsigned int ccsubs[] = {
  VEOF,
  VEOL,
  VERASE,
  VINTR,
  VKILL,
  VMIN,
  VQUIT,
  VSTART,
  VSTOP,
  VSUSP,
  VTIME,
  NCCS
};

tcflag_t iflags[] = {
  BRKINT,
  ICRNL,
  IGNBRK,
  IGNCR,
  IGNPAR,
  INLCR,
  INPCK,
  ISTRIP,
  IXOFF,
  IXON,
  PARMRK,
};

tcflag_t oflags[] = {
  OPOST,
};

tcflag_t cflags[] = {
  CSIZE,
  CS5,
  CS6,
  CS7,
  CS8,
  CSTOPB,
  CREAD,
  PARENB,
  PARODD,
  HUPCL,
  CLOCAL,
};

tcflag_t lflags[] = {
  ECHO,
  ECHOE,
  ECHOK,
  ECHONL,
  ICANON,
  IEXTEN,
  ISIG,
  NOFLSH,
  TOSTOP,
};

speed_t rates[] = {
  B0,
  B50,
  B75,
  B110,
  B134,
  B150,
  B200,
  B300,
  B600,
  B1200,
  B1800,
  B2400,
  B4800,
  B9600,
  B19200,
  B38400,
};

int opts[] = {
  TCSANOW,
  TCSADRAIN,
  TCSAFLUSH,
  TCIFLUSH,
  TCOFLUSH,
  TCIOFLUSH,
  TCIOFF,
  TCION,
  TCOOFF,
  TCOON
};

void f(struct termios *aa, const struct termios *bb, int cc)
{
  speed_t a = cfgetispeed(bb);
  speed_t b = cfgetospeed(bb);
  int     c = cfsetispeed(aa, B134);
  int     d = cfsetospeed(aa, B300);
  int     e = tcdrain(cc);
  int     f = tcflow(cc, TCIOFF);
  int     g = tcflush(cc, TCOFLUSH);
  int     h = tcgetattr(cc, aa);
  int     j = tcsendbreak(cc, 0);
  int     k = tcsetattr(cc, TCSANOW, aa);
}
