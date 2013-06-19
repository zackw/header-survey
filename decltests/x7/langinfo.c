/* <code>nl_langinfo_l</code> */
#include <langinfo.h>

char *(*a)(nl_item, locale_t) = nl_langinfo_l;
