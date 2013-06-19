#include <tar.h>

/* nothing actually says these are macros but let's assume they are till
   proven otherwise; in a header this old it's unlikely anyone would have
   used anything else */

#if !defined TSUID || TSUID != 04000
#error "TSUID"
#endif
#if !defined TSGID || TSGID != 02000
#error "TSGID"
#endif
#if !defined TUREAD || TUREAD != 00400
#error "TUREAD"
#endif
#if !defined TUWRITE || TUWRITE != 00200
#error "TUWRITE"
#endif
#if !defined TUEXEC || TUEXEC != 00100
#error "TUEXEC"
#endif
#if !defined TGREAD || TGREAD != 00040
#error "TGREAD"
#endif
#if !defined TGWRITE || TGWRITE != 00020
#error "TGWRITE"
#endif
#if !defined TGEXEC || TGEXEC != 00010
#error "TGEXEC"
#endif
#if !defined TOREAD || TOREAD != 00004
#error "TOREAD"
#endif
#if !defined TOWRITE || TOWRITE != 00002
#error "TOWRITE"
#endif
#if !defined TOEXEC || TOEXEC != 00001
#error "TOEXEC"
#endif

#if !defined REGTYPE || REGTYPE != '0'
#error "REGTYPE"
#endif
#if !defined AREGTYPE || AREGTYPE != '\0'
#error "AREGTYPE"
#endif
#if !defined LNKTYPE || LNKTYPE != '1'
#error "LNKTYPE"
#endif
#if !defined SYMTYPE || SYMTYPE != '2'
#error "SYMTYPE"
#endif
#if !defined CHRTYPE || CHRTYPE != '3'
#error "CHRTYPE"
#endif
#if !defined BLKTYPE || BLKTYPE != '4'
#error "BLKTYPE"
#endif
#if !defined DIRTYPE || DIRTYPE != '5'
#error "DIRTYPE"
#endif
#if !defined FIFOTYPE || FIFOTYPE != '6'
#error "FIFOTYPE"
#endif
#if !defined CONTTYPE || CONTTYPE != '7'
#error "CONTTYPE"
#endif


#if !defined TMAGLEN || TMAGLEN != 6
#error "TMAGLEN"
#endif
#if !defined TVERSLEN || TVERSLEN != 2
#error "TVERSLEN"
#endif

/* these are required to be string literals
   there is no practical way to check their contents */

const char *magic = ""TMAGIC"";
const char *versn = ""TVERSION"";
