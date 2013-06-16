/* baseline */
#include <pwd.h>

void f(const char *bb, uid_t cc)
{
  struct passwd aa;
  char **aan = &aa.pw_name;
  uid_t *aap = &aa.pw_uid;
  gid_t *aag = &aa.pw_gid;
  char **aad = &aa.pw_dir;
  char **aas = &aa.pw_shell;

  struct passwd *a = getpwnam(bb);
  struct passwd *b = getpwuid(cc);
  struct passwd *c = getpwent();

  struct passwd *dd;
  char ee[512];
  int d = getpwnam_r(bb, &aa, ee, sizeof ee, &dd);
  int e = getpwuid_r(cc, &aa, ee, sizeof ee, &dd);

  setpwent();
  endpwent();
}
