# This makefile trial-compiles all the test files, for debugging.
# It assumes GCC/Clang command line option syntax and uses GNU Make
# extensions.

TESTS := $(wildcard *.ini)
C     := $(TESTS:.ini=.c)
O     := $(TESTS:.ini=.o)

# All files (even those that are nominally tests of C89) are compiled
# with the compiler set to C99 mode, because we're counting stuff from
# the 1995 amendment to C89 as C89, but some systems treat that as C99
# material.

CFLAGS = -O -std=c99 -pedantic -W -Wall -Wno-deprecated-declarations -Werror

trial: $(O)

%.c: %.ini Maketest.py
	python Maketest.py $< $@

clean:
	-rm -f $(O) $(C)

.PHONY: trial clean
.PRECIOUS: $(C)
