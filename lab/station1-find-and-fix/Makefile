CC      ?= gcc
CFLAGS  ?= -Wall -Wextra -O1 -g -fno-omit-frame-pointer -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0
ASAN     = -fsanitize=address,undefined

all: recparse recparse-asan

recparse: recparse.c
	$(CC) $(CFLAGS) -o $@ $<

recparse-asan: recparse.c
	$(CC) $(CFLAGS) $(ASAN) -o $@ $<

inputs: mkinputs.py
	python3 mkinputs.py

check: recparse-asan inputs
	./check.sh

clean:
	rm -f recparse recparse-asan

.PHONY: all inputs check clean
