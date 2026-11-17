CC      = gcc
CFLAGS  = -Wall -Wextra -O1 -g
TARGET  = heartbleed

all: $(TARGET)

$(TARGET): heartbleed.c
	$(CC) $(CFLAGS) -o $@ $<
	strip $@

debug: heartbleed.c
	$(CC) $(CFLAGS) -o heartbleed-dbg $<

asan: heartbleed.c
	$(CC) $(CFLAGS) -fsanitize=address -o heartbleed-asan $<

clean:
	rm -f $(TARGET) heartbleed-dbg heartbleed-asan trigger.bin

.PHONY: all debug asan clean
