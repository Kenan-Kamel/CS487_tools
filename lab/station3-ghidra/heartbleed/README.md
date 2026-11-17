# Heartbleed demo — Ghidra + LLM reverse engineering

A minimal binary reproducing the **CVE-2014-0160 (Heartbleed)** vulnerability
pattern. Students import the stripped binary into Ghidra and use an LLM to
find and explain the memory-disclosure bug.

## Setup

```bash
make                    # builds and strips ./heartbleed
python3 trigger.py      # creates trigger.bin (malicious heartbeat)
```

Import `heartbleed` into Ghidra, run auto-analysis, enable GhidraMCP.

## Ghidra + LLM prompts (10–15 min)

1. **"What does this binary do? Start from main."**
   The LLM should identify the file-reading logic, the record-type switch, and
   the two handlers.

2. **"Describe the struct that main allocates on the stack."**
   It should reconstruct the `session` struct: a 256-byte buffer, an int, then
   three string fields.

3. **"Find security vulnerabilities in the heartbeat handler."**
   The LLM should spot the missing bounds check: `payload_len` comes from the
   input but `memcpy` trusts it, reading past the buffer into the token,
   username, and password fields.

4. **"What data could an attacker leak, and how?"**
   It should explain that a short payload with a large claimed length causes
   the response to include the struct's secret fields.

5. **"Rename the decompiled functions and variables."**
   Shows how the LLM turns `FUN_00401234` into readable code.

## Trigger the bug

```bash
./heartbleed trigger.bin | xxd | head -30
```

Look for `sk-prod-`, `admin`, and `Tr0ub4dor&3` in the hex dump — that is
the leaked session data.

## Ground truth

See `heartbleed.c` for the source. The vulnerability is at the `memcpy` in
`handle_heartbeat`: it copies `payload_len` bytes (client-controlled) instead
of `recv_len - 3` bytes (actual payload size).

**Fix:** add `if (payload_len > s->recv_len - 3) return -1;` before the copy.
This is exactly what the OpenSSL patch for CVE-2014-0160 did.
