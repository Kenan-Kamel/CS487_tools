#!/usr/bin/env python3
"""Brute-force a valid key for keycheck (so the instructor has one ready)."""
import itertools, string
def h(k):
    v = 2166136261
    for c in k:
        if c != '-':
            v = ((v ^ ord(c)) * 16777619) & 0xffffffff
    return v
for a in itertools.product(string.ascii_uppercase, repeat=4):
    k = "".join(a) + "-UIC4-87"
    if len(k) == 12 and h(k) % 1000 == 487:
        print(k); break
