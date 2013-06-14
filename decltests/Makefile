# This makefile trial-compiles all the test files, for debugging.
# It assumes GCC/Clang command line option syntax and uses GNU Make
# extensions.

C89_TESTS := $(wildcard *-c89.c */*-c89.c)
C99_TESTS := $(wildcard *-c99.c */*-c99.c)
X5_TESTS  := $(wildcard *-x5.c  */*-x5.c)
X6_TESTS  := $(wildcard *-x6.c  */*-x6.c)
X7_TESTS  := $(wildcard *-x7.c  */*-x7.c)

ALL_TESTS := $(C89_TESTS) $(C99_TESTS) $(X5_TESTS) $(X6_TESTS) $(X7_TESTS)

X5_O      := $(patsubst %.c,%.o,$(X5_TESTS))
X6_O      := $(patsubst %.c,%.o,$(X6_TESTS))
X7_O      := $(patsubst %.c,%.o,$(X7_TESTS))
ALL_O     := $(patsubst %.c,%.o,$(ALL_TESTS))

# All files (even those that are nominally tests of C89) are compiled
# with the compiler set to C99 mode, because we're counting stuff from
# in the 1995 amendment to C89 as C89, but some systems treat that as
# C99 material.

CFLAGS = -O -std=c99 -pedantic -W -Wall -Wno-unused -Wno-unused-parameter \
-Wno-unknown-pragmas -Wno-deprecated-declarations -Werror

$(X5_O): CPPFLAGS = -D_XOPEN_SOURCE=500
$(X6_O): CPPFLAGS = -D_XOPEN_SOURCE=600
$(X7_O): CPPFLAGS = -D_XOPEN_SOURCE=700

trial: $(ALL_O)
clean:
	-rm -f $(ALL_O)

.PHONY: trial clean
