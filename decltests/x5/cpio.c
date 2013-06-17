#include <cpio.h>

/* this is required to be a macro that expands to a string literal;
   there is no practical way to check its contents */
const char *magic = ""MAGIC"";

/* nothing actually says these are macros but let's assume they are till
   proven otherwise; in a header this old it's unlikely anyone would have
   used an enum */

#if C_IRUSR != 0000400
#error "C_IRUSR"
#endif

#if C_IWUSR != 0000200
#error "C_IWUSR"
#endif

#if C_IXUSR != 0000100
#error "C_IXUSR"
#endif

#if C_IRGRP != 0000040
#error "C_IRGRP"
#endif

#if C_IWGRP != 0000020
#error "C_IWGRP"
#endif

#if C_IXGRP != 0000010
#error "C_IXGRP"
#endif

#if C_IROTH != 0000004
#error "C_IROTH"
#endif

#if C_IWOTH != 0000002
#error "C_IWOTH"
#endif

#if C_IXOTH != 0000001
#error "C_IXOTH"
#endif

#if C_ISUID != 0004000
#error "C_ISUID"
#endif

#if C_ISGID != 0002000
#error "C_ISGID"
#endif

#if C_ISVTX != 0001000
#error "C_ISVTX"
#endif

#if C_ISDIR != 0040000
#error "C_ISDIR"
#endif

#if C_ISFIFO !=0010000
#error "C_ISFIFO"
#endif

#if C_ISREG != 0100000
#error "C_ISREG"
#endif

#if C_ISBLK != 0060000
#error "C_ISBLK"
#endif

#if C_ISCHR != 0020000
#error "C_ISCHR"
#endif

#if C_ISCTG != 0110000
#error "C_ISCTG"
#endif

#if C_ISLNK != 0120000
#error "C_ISLNK"
#endif

#if C_ISSOCK !=0140000
#error "C_ISSOCK"
#endif
