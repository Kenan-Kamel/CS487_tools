/*
 * recparse.c - a tiny record-file parser (CS 487 lab program)
 *
 * File format: a sequence of records, each
 *     name      NUL-terminated string
 *     len       4-byte little-endian integer
 *     data      len bytes
 *
 * Usage: ./recparse FILE
 *
 * This program has bugs. Find them, fix them, then try to break your fix.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAX_DATA 64

struct record {
    char     name[32];
    uint8_t  data[MAX_DATA];
    int32_t  len;
};

static long read_file(const char *path, uint8_t **out)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return -1; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    rewind(f);
    uint8_t *buf = malloc(n);
    if (fread(buf, 1, n, f) != (size_t)n) { perror("fread"); return -1; }
    fclose(f);
    *out = buf;
    return n;
}

/* Parse one record starting at p. Returns bytes consumed, or -1. */
static long parse_record(const uint8_t *p, long avail, struct record *r)
{
    const char *name = (const char *)p;
    size_t name_len = strnlen(name, avail);
    if ((long)name_len == avail) return -1;        /* no NUL in range */

    if (name_len >= sizeof r->name) {
        fprintf(stderr, "name too long (%zu)\n", name_len);
        return -1;
    }
    memcpy(r->name, name, name_len + 1);
    p += name_len + 1;
    avail -= name_len + 1;

    if (avail < 4) return -1;
    int32_t len;
    memcpy(&len, p, 4);
    p += 4;
    avail -= 4;

    if (len < 0 || len > MAX_DATA) {
        fprintf(stderr, "record too long (%d)\n", len);
        return -1;
    }
    if (len > avail) return -1;

    memcpy(r->data, p, len);
    r->len = len;
    return name_len + 1 + 4 + len;
}

static void print_record(const struct record *r)
{
    printf("record: name=\"%s\" len=%d data=", r->name, r->len);
    for (int i = 0; i < r->len && i < 16; i++) printf("%02x", r->data[i]);
    if (r->len > 16) printf("...");
    printf("\n");
}

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "usage: %s FILE\n", argv[0]); return 2; }

    uint8_t *buf;
    long n = read_file(argv[1], &buf);
    if (n < 0) return 1;

    long off = 0;
    int count = 0;
    while (off < n) {
        struct record r;
        memset(&r, 0, sizeof r);
        long used = parse_record(buf + off, n - off, &r);
        if (used < 0) { fprintf(stderr, "bad record at offset %ld\n", off); break; }
        print_record(&r);
        off += used;
        count++;
    }
    printf("%d record(s)\n", count);
    free(buf);
    return 0;
}
