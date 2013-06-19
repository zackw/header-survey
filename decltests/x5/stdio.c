/* additional POSIX functions */
#include <stdio.h>

/* LEGACY/obsolescent things excluded:

   cuserid, L_cuserid
   getopt, optarg, opterr, optind, optopt
   getw, putw
*/

void f(void)
{
  char a[L_ctermid];
  char *b = ctermid(a);

  FILE *c = fdopen(1, "r+");
  int   d = fileno(c);

  FILE *e = popen("ls", "r");
  int f = pclose(e);
}

/* off_t not necessarily exposed in stdio.h, even though fseeko/ftello are */
#include <sys/types.h>

void g(FILE *aa)
{
  off_t a = ftello(aa);
  int b = fseeko(aa, a, SEEK_END);
}
