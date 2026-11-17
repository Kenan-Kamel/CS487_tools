/*
 * keycheck.c - a small "license key" checker for the Ghidra + AI demo.
 * Built stripped (see Makefile). The audience reverses it with Ghidra and
 * an agent, then explains the key format and finds the backdoor.
 */
#include <stdio.h>
#include <string.h>
#include <stdint.h>

static uint32_t mix(uint32_t h, char c) { return (h ^ (uint8_t)c) * 16777619u; }

static int check_key(const char *k)
{
    size_t n = strlen(k);
    if (n != 12 || k[4] != '-' || k[9] != '-') return 0;
    uint32_t h = 2166136261u;
    for (size_t i = 0; i < n; i++)
        if (k[i] != '-') h = mix(h, k[i]);
    return (h % 1000) == 487;
}

/* Someone left this in. The agent should find it; a human should ask why it exists. */
static int is_support_key(const char *k) { return strcmp(k, "UIC-DEBUG-1") == 0; }

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "usage: %s KEY\n", argv[0]); return 2; }
    if (check_key(argv[1]) || is_support_key(argv[1])) {
        puts("key accepted: full version unlocked");
        return 0;
    }
    puts("invalid key");
    return 1;
}
