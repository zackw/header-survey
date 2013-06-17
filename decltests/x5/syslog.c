#include <syslog.h>

int facil[] = {
  LOG_KERN,
  LOG_USER,
  LOG_MAIL,
  LOG_NEWS,
  LOG_UUCP,
  LOG_DAEMON,
  LOG_AUTH,
  LOG_CRON,
  LOG_LPR,
  LOG_LOCAL0,
  LOG_LOCAL1,
  LOG_LOCAL2,
  LOG_LOCAL3,
  LOG_LOCAL4,
  LOG_LOCAL5,
  LOG_LOCAL6,
  LOG_LOCAL7
};

int sev[] = {
  LOG_EMERG,
  LOG_ALERT,
  LOG_CRIT,
  LOG_ERR,
  LOG_WARNING,
  LOG_NOTICE,
  LOG_INFO,
  LOG_DEBUG
};

int opt[] = {
  LOG_PID,
  LOG_CONS,
  LOG_NDELAY,
  LOG_ODELAY,
  LOG_NOWAIT
};

void f(void)
{
  openlog("me", LOG_PID|LOG_CONS|LOG_NDELAY|LOG_NOWAIT, LOG_LOCAL0);
  int a = setlogmask(LOG_MASK(LOG_NOTICE));
  syslog(LOG_WARNING, "a with the %d with the %s", 73, "glue");
  closelog();
}
