/*
 * heartbleed.c — minimal reproduction of the CVE-2014-0160 (Heartbleed) pattern.
 *
 * A tiny "session server" that reads a binary heartbeat record from a file
 * and echoes the payload back. The bug: it trusts the client-specified
 * payload length instead of the actual received length, so a short payload
 * with a large claimed length leaks adjacent memory — in this case the
 * session's auth token, username, and password.
 *
 * Build stripped for Ghidra:  make
 * Trigger the leak:           python3 trigger.py && ./heartbleed trigger.bin | xxd
 *
 * CS 487 — AI as a Security Teammate
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define HEARTBEAT_REQUEST  1
#define HEARTBEAT_RESPONSE 2
#define STATUS_REQUEST     3

struct session {
    uint8_t  recv_buf[256];
    int      recv_len;
    char     auth_token[64];
    char     username[32];
    char     password[32];
};

static void init_session(struct session *s)
{
    memset(s, 0, sizeof *s);
    strcpy(s->auth_token, "sk-prod-a7f3b2c1d4e5f609876");
    strcpy(s->username, "admin");
    strcpy(s->password, "Tr0ub4dor&3");
}

static int handle_heartbeat(struct session *s, FILE *out)
{
    if (s->recv_len < 3) return -1;

    uint16_t payload_len = ((uint16_t)s->recv_buf[1] << 8) | s->recv_buf[2];

    uint8_t *resp = malloc(3 + payload_len);
    if (!resp) return -1;

    resp[0] = HEARTBEAT_RESPONSE;
    resp[1] = s->recv_buf[1];
    resp[2] = s->recv_buf[2];

    /* BUG: copies payload_len bytes, but actual payload may be shorter.
       Reads past recv_buf into auth_token, username, password. */
    memcpy(resp + 3, s->recv_buf + 3, payload_len);

    fwrite(resp, 1, 3 + (size_t)payload_len, out);
    free(resp);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: %s <record-file>\n", argv[0]);
        return 2;
    }

    struct session sess;
    init_session(&sess);

    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 1; }

    sess.recv_len = fread(sess.recv_buf, 1, sizeof sess.recv_buf, f);
    fclose(f);

    int ret;
    switch (sess.recv_buf[0]) {
    case HEARTBEAT_REQUEST:
        ret = handle_heartbeat(&sess, stdout);
        break;
    case STATUS_REQUEST:
        fprintf(stdout, "STATUS: OK\n");
        ret = 0;
        break;
    default:
        fprintf(stderr, "unknown record type %d\n", sess.recv_buf[0]);
        ret = -1;
    }

    return ret < 0 ? 1 : 0;
}
