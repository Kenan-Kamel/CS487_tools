# Lab materials · AI as a Security Teammate (CS 487)

Three stations, each can be instructor demo or student-driven.

| Station | Directory | What happens | Needs |
|---|---|---|---|
| 1 | `station2-packets/` | agent summarizes and questions a pcap | tshark, Claude Code |
| 2 | `station3-ghidra/` | agent reverses stripped binaries in Ghidra (keycheck warm-up + Heartbleed main) | Ghidra 12.1.4, GhidraMCP, Claude Code |
| 3 | `detect-with-llm/` | students compare static analyzers vs LLM on a buggy C program | gcc, flawfinder, cppcheck, Claude |

## Setup in the SEED VM (Ubuntu 20.04)

**Claude Code.** The native installer needs no Node.js and lists Ubuntu 20.04 as
supported. Smoke-test on one VM before class.

```sh
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

If `claude` segfaults on the 20.04 glibc, pin an older build:
`curl -fsSL https://claude.ai/install.sh | bash -s 2.1.245`.

**Class key.** Each student runs, in the shell where they start `claude`:

```sh
export ANTHROPIC_API_KEY=sk-ant-...   # handed out in class
claude
```

Claude Code asks once whether to use the key from the environment; answer yes
and it skips the login prompt. Create the key in the Anthropic Console with the
"Claude Code" role, set a spend limit, and revoke it after the lecture.

**Analyzers.**

```sh
pip3 install flawfinder            # works on Python 3.8
sudo apt install -y cppcheck tshark
```

**Ghidra (station 2).** Ghidra 12.1.4 from github.com/NationalSecurityAgency/ghidra/releases,
then the GhidraMCP 2.0 extension zip from github.com/LaurieWired/GhidraMCP/releases:
File → Install Extensions → + → pick the zip → restart Ghidra → File → Configure →
Developer → enable GhidraMCPPlugin. Then register the server with Claude Code:

```sh
pip3 install uv     # or pipx; GhidraMCP's Python side wants 3.10+, uv fetches one
claude mcp add ghidra -- uvx --from git+https://github.com/LaurieWired/GhidraMCP ghidra-mcp --ghidra-server http://127.0.0.1:8080/
```

Fallback if MCP misbehaves on the day: in Ghidra, export the decompiled C
(File → Export Program → C/C++) and hand that file to Claude Code. Same
prompts, same lesson.

## Before class checklist

- [ ] `claude --version` works in the SEED VM
- [ ] Class key created, spend limit set, copied somewhere you can read aloud
- [ ] `tshark -r lab/station2-packets/demo.pcap -q -z conv,tcp` prints conversations
- [ ] `lab/station3-ghidra/keycheck` built and imported into Ghidra, auto-analysis done
- [ ] `cd lab/station3-ghidra/heartbleed && make && python3 trigger.py` builds the Heartbleed binary
- [ ] `lab/detect-with-llm/urlparse` builds with `make`
- [ ] Projector laptop has `claude` logged in with your own account, not the class key
