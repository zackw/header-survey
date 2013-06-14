/* baseline */
#include <dlfcn.h>

void f(void)
{
  void *a = dlopen("liba.so", RTLD_LAZY|RTLD_GLOBAL);
  void *b = dlopen("libb.so", RTLD_NOW|RTLD_LOCAL);

  void *c = dlsym(a, "symbol");
  int   e = dlclose(a);
  char *f = dlerror();
}
