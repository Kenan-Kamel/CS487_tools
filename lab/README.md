# Lab materials · AI as a Security Teammate (CS 487)

Two stations, both using Ghidra + an LLM to reverse-engineer stripped binaries.
No API key required — paste decompiled code into claude.ai or ChatGPT.

**Run the full demo:**  `bash lab/demo.sh`

| Station | Directory | What happens | Time |
|---|---|---|---|
| 1 | `station3-ghidra/heartbleed/` | Reverse-engineer a Heartbleed (CVE-2014-0160) binary, find the memory leak | 15 min |
| 2 | `station3-ghidra/` | Reverse-engineer a keycheck binary, find the FNV-1a hash and the backdoor | 10 min |

## Setup

**Ghidra:** Ghidra 12.1.4 from github.com/NationalSecurityAgency/ghidra/releases.

Optionally install GhidraMCP for agentic analysis with Claude Code:
```sh
pip3 install uv
claude mcp add ghidra -- uvx --from git+https://github.com/LaurieWired/GhidraMCP ghidra-mcp --ghidra-server http://127.0.0.1:8080/
```

**Fallback (no MCP):** in Ghidra, export decompiled C (File → Export Program → C/C++)
and paste it into claude.ai or ChatGPT. Same prompts, same lesson.

## Before class checklist

- [ ] Ghidra 12.1.4 installed
- [ ] `cd lab/station3-ghidra && make` builds `keycheck`
- [ ] `cd lab/station3-ghidra/heartbleed && make && python3 trigger.py` builds `heartbleed`
- [ ] Both binaries imported into Ghidra, auto-analysis done
- [ ] `bash lab/demo.sh` runs end-to-end on the projector laptop
