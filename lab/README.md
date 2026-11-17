# Lab materials · AI as a Security Teammate (CS 487)

Three stations. Station 1 is for students. Stations 2 and 3 are instructor
demos by default; each has a runbook so either can be student-driven.

| Station | Directory | What happens | Needs |
|---|---|---|---|
| 1 | `station1-find-and-fix/` | static analysis + agent finds and patches `recparse.c`, students break the patch | gcc, Claude Code, flawfinder (optional cppcheck, Semgrep) |
| 2 | `station2-packets/` | agent summarizes and questions a pcap | tshark, Claude Code |
| 3 | `station3-ghidra/` | agent drives Ghidra on a stripped binary | Ghidra 12.1.4, GhidraMCP, Claude Code |

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
# Semgrep needs Python 3.10+, so use Docker in the SEED VM:
docker pull semgrep/semgrep
docker run --rm -v "$PWD:/src" semgrep/semgrep semgrep scan --config p/c
```

**Ghidra (station 3 only).** Ghidra 12.1.4 from github.com/NationalSecurityAgency/ghidra/releases,
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
- [ ] `cd lab/station1-find-and-fix && make inputs && make && ./check.sh` shows 3 FAIL
- [ ] `tshark -r lab/station2-packets/demo.pcap -q -z conv,tcp` prints 4 conversations
- [ ] `lab/station3-ghidra/keycheck` built and imported into Ghidra, auto-analysis done
- [ ] Projector laptop has `claude` logged in with your own account, not the class key
