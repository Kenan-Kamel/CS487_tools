# Station 3 · An agent drives Ghidra

`keycheck` is a stripped, PIE x86-64 binary built from `keycheck.c`. It
accepts a 12-character license key of the form `XXXX-XXXX-XX`, validated
with an FNV-1a hash, and also accepts one hard-coded support key.
`findkey.py` brute-forces a valid key so you have one ready.

```sh
make                      # builds ./keycheck (stripped)
python3 findkey.py        # prints a valid key, e.g. ABEL-UIC4-87
./keycheck ABEL-UIC4-87   # key accepted
```

## Runbook (10 min)

Before class: import `keycheck` into Ghidra 12.1.4, run auto-analysis, enable
GhidraMCP, register it with `claude mcp add ghidra ...` (see `../README.md`).

Prompts:

1. "What does this program check? Start from main."
2. "Describe the key format and the validation function in plain English."
3. "Is there any way to get 'key accepted' without a valid key?"
4. "Rename the functions and variables to match what they do."
5. "Give me a key that passes." (It will offer to brute-force. Let it, or show `findkey.py`.)

What to point out:

- It identifies FNV-1a from the two constants. Make it show the decompiled line, not just assert it.
- It finds the second accept path (a string compare). Ask the room: should this exist, and who would you ask? A model can find the backdoor; it cannot tell you whether it is authorized.
- Renaming is where the agent earns its keep: the decompiler output becomes readable in one prompt.

## Fallback

If MCP is flaky, export the decompiled C from Ghidra (File → Export Program →
C/C++) and give the file to Claude Code. Same prompts, same lesson.
