#!/usr/bin/env python3
"""Generate test inputs for recparse into ./inputs. Run: python3 mkinputs.py"""
import struct, os

def rec(name: bytes, data: bytes, len_override=None):
    n = len(data) if len_override is None else len_override
    return name + b"\0" + struct.pack("<i", n) + data

os.makedirs("inputs", exist_ok=True)
def w(f, b):
    with open(os.path.join("inputs", f), "wb") as fh:
        fh.write(b)

# good.bin: a well-formed file with two records. Must keep working after any fix.
w("good.bin", rec(b"alice", b"hello") + rec(b"bob", bytes(range(20))))

# crash-name.bin: a 200-byte name. Stack buffer overflow via strcpy.
w("crash-name.bin", rec(b"A" * 200, b"x"))

# crash-neglen.bin: len = -1. Does the length check reject it?
w("crash-neglen.bin", rec(b"eve", b"", len_override=-1))

# short.bin: len says 60 bytes but only 3 follow. Should be rejected cleanly.
w("short.bin", rec(b"carol", b"abc", len_override=60))

# leak-name32.bin: a name of exactly 32 bytes, then data that should never be
# printed as part of the name. Compare the printed name before and after a fix.
w("leak-name32.bin", rec(b"B" * 32, b"SECRET-DATA-FROM-THE-NEXT-FIELD"))
print("wrote", sorted(os.listdir("inputs")))
