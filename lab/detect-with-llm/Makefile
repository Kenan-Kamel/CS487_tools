CC      = gcc
CFLAGS  = -Wall -Wextra -g
TARGET  = urlparse

all: $(TARGET)

$(TARGET): urlparse.c
	$(CC) $(CFLAGS) -o $@ $<

asan: urlparse.c
	$(CC) $(CFLAGS) -fsanitize=address -o urlparse-asan $<

clean:
	rm -f $(TARGET) urlparse-asan

.PHONY: all asan clean
