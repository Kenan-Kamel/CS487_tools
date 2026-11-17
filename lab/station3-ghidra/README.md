# Station 2 · Ghidra + LLM reverse engineering

Two exercises: a warm-up (keycheck) and a main challenge (Heartbleed).

## Exercise A — keycheck (5 min warm-up)

`keycheck` is a stripped, PIE x86-64 binary built from `keycheck.c`. It
accepts a 12-character license key of the form `XXXX-XXXX-XX`, validated
with an FNV-1a hash, and also accepts one hard-coded support key.
`findkey.py` brute-forces a valid key so you have one ready.

```sh
make                      # builds ./keycheck (stripped)
python3 findkey.py        # prints a valid key, e.g. ABEL-UIC4-87
./keycheck ABEL-UIC4-87   # key accepted
```

Prompts:

1. "What does this program check? Start from main."
2. "Is there any way to get 'key accepted' without a valid key?"
3. "Rename the functions and variables to match what they do."

What to point out:
- It identifies FNV-1a from the two constants (2166136261, 16777619)
- It finds the backdoor (a string compare). Ask the room: should this exist?
- Renaming is where the agent earns its keep: decompiler output becomes readable

## Exercise B — Heartbleed (10–15 min main challenge)

A minimal binary reproducing the **CVE-2014-0160 (Heartbleed)** pattern.
Students find a memory-disclosure bug in a session handler.

```sh
cd heartbleed
make                      # builds and strips ./heartbleed
python3 trigger.py        # creates malicious input
```

Import `heartbleed` into Ghidra, run auto-analysis.

Prompts:

1. "What does this binary do? Start from main."
2. "Describe the struct that main allocates on the stack."
3. "Find security vulnerabilities in the heartbeat handler."
4. "What data could an attacker leak, and how?"
5. "Rename the decompiled functions and variables."

Trigger the leak to prove it:
```sh
./heartbleed trigger.bin | xxd | head -30
# Look for: sk-prod-..., admin, Tr0ub4dor&3
```

See `heartbleed/README.md` for the full walkthrough.

## Setup

Before class: import both binaries into Ghidra 12.1.4, run auto-analysis, enable
GhidraMCP, register it with `claude mcp add ghidra ...` (see `../README.md`).

## Fallback

If MCP is flaky, export the decompiled C from Ghidra (File → Export Program →
C/C++) and give the file to Claude Code. Same prompts, same lesson.
