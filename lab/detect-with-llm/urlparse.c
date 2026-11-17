/*
 * urlparse.c - a small URL parser and query-string decoder (CS 487 lab)
 *
 * Usage: ./urlparse "http://example.com/path?key=value&name=alice"
 *
 * This program has security bugs. How many can you find?
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_PARAMS 8

struct param { char key[64]; char value[128]; };

struct url {
    char scheme[16];
    char host[128];
    char path[256];
    struct param params[MAX_PARAMS];
    int  n_params;
};

/* Percent-decode in place: %41 -> 'A', + -> ' '. */
static void url_decode(char *s)
{
    char *o = s;
    while (*s) {
        if (s[0] == '%' && isxdigit(s[1]) && isxdigit(s[2])) {
            char hex[3] = { s[1], s[2], 0 };
            *o++ = (char)strtol(hex, NULL, 16);
            s += 3;
        } else if (*s == '+') {
            *o++ = ' '; s++;
        } else {
            *o++ = *s++;
        }
    }
    *o = '\0';
}

static int parse_url(const char *raw, struct url *u)
{
    memset(u, 0, sizeof *u);

    const char *sep = strstr(raw, "://");
    if (!sep) return -1;

    /* scheme */
    strcpy(u->scheme, raw);
    u->scheme[sep - raw] = '\0';

    /* host and path */
    const char *hp = sep + 3;
    const char *slash = strchr(hp, '/');
    const char *qmark = strchr(hp, '?');

    if (slash) {
        int hlen = slash - hp;
        if (hlen > 127) hlen = 127;
        memcpy(u->host, hp, hlen);
        u->host[hlen] = '\0';

        const char *pend = qmark ? qmark : hp + strlen(hp);
        int plen = pend - slash;
        if (plen > 255) plen = 255;
        memcpy(u->path, slash, plen);
        u->path[plen] = '\0';
    } else {
        int hlen = qmark ? (int)(qmark - hp) : (int)strlen(hp);
        strncpy(u->host, hp, hlen);
        u->host[hlen] = '\0';
        strcpy(u->path, "/");
    }

    /* query string */
    if (qmark) {
        char *qs = strdup(qmark + 1);
        char *tok = strtok(qs, "&");
        while (tok && u->n_params < MAX_PARAMS) {
            char *eq = strchr(tok, '=');
            if (eq) {
                *eq = '\0';
                url_decode(tok);
                url_decode(eq + 1);
                strncpy(u->params[u->n_params].key, tok, 63);
                u->params[u->n_params].key[63] = '\0';
                strncpy(u->params[u->n_params].value, eq + 1, 127);
                u->params[u->n_params].value[127] = '\0';
                u->n_params++;
            }
            tok = strtok(NULL, "&");
        }
        free(qs);
    }

    return 0;
}

static int is_safe_path(const char *path)
{
    return strstr(path, "..") == NULL;
}

static void print_url(const struct url *u)
{
    printf("scheme: %s\nhost:   %s\npath:   %s\n", u->scheme, u->host, u->path);
    for (int i = 0; i < u->n_params; i++) {
        printf("  ");
        printf(u->params[i].key);
        printf(" = %s\n", u->params[i].value);
    }
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: %s URL\n", argv[0]);
        return 2;
    }

    struct url u;
    if (parse_url(argv[1], &u) < 0) {
        fprintf(stderr, "bad url\n");
        return 1;
    }

    if (!is_safe_path(u.path)) {
        fprintf(stderr, "unsafe path\n");
        return 1;
    }
    url_decode(u.path);

    print_url(&u);
    return 0;
}
