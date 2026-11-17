all: keycheck
keycheck: keycheck.c
	gcc -O1 -s -fno-stack-protector -o keycheck keycheck.c
clean:
	rm -f keycheck
