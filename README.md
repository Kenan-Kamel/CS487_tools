# CS 487: AI for Security — Lecture & Lab Materials

Slide deck and two hands-on labs for the **AI as a Security Teammate** lecture.
No API key needed — students paste code into [claude.ai](https://claude.ai) (free).

## One-command setup

```bash
curl -fsSL https://raw.githubusercontent.com/Kenan-Kamel/CS487_tools/main/setup.sh | bash
```

This clones the repo, installs Ghidra (if missing), builds the lab binaries,
and opens the slides. Or do it manually:

```bash
git clone https://github.com/Kenan-Kamel/CS487_tools.git
cd CS487_tools
bash setup.sh
```

---

## Lab 1 — Heartbleed (5 min)

**Goal:** Reverse-engineer a stripped binary and find a memory-disclosure
vulnerability (CVE-2014-0160 pattern).

### What's inside

A tiny "session server" that echoes heartbeat messages. The bug: it trusts
the client-specified payload length instead of checking the actual size.
A short payload with a large claimed length leaks the server's auth token,
username, and password from adjacent memory.

### Step by step

1. **Open Ghidra** and import `lab/station3-ghidra/heartbleed/heartbleed`
2. **Run auto-analysis** (yes to all defaults)
3. **Double-click `main`** in the Symbol Tree → you see decompiled C
4. **Select all the decompiled code** → Copy
5. **Go to [claude.ai](https://claude.ai)** (free, no API key) and paste with this prompt:

   > This is decompiled C from a stripped binary. Find all security
   > vulnerabilities. For each one, explain the bug, how to exploit it,
   > and how to fix it.

6. **Read the LLM's response** — it should find:
   - The `memcpy` copies `payload_len` bytes (client-controlled)
   - But the actual payload may be much shorter
   - This leaks adjacent struct fields (token, username, password)

7. **Prove it in the terminal:**
   ```bash
   cd lab/station3-ghidra/heartbleed
   ./heartbleed trigger.bin | xxd | head -30
   ```

### Expected output

```
00000100: 0700 0000 736b 2d70 726f 642d 6137 6633  ....sk-prod-a7f3
00000110: 6232 6331 6434 6535 6636 3039 3837 3600  b2c1d4e5f609876.
00000140: 0000 0000 6164 6d69 6e00 0000 0000 0000  ....admin.......
00000160: 0000 0000 5472 3075 6234 646f 7226 3300  ....Tr0ub4dor&3.
```

The auth token, username, and password are leaked in the response.

### The fix (one line)

```c
if (payload_len > s->recv_len - 3) return -1;
```

This is exactly what the OpenSSL patch for CVE-2014-0160 added.

---

## Lab 2 — Keycheck backdoor (5 min)

**Goal:** Reverse-engineer a stripped license-key checker and find a
hidden backdoor.

### What's inside

A program that validates 12-character keys (`XXXX-XXXX-XX`) using FNV-1a
hashing. But there's a second code path: a `strcmp` against a hard-coded
string that bypasses the hash entirely.

### Step by step

1. **Open Ghidra** and import `lab/station3-ghidra/keycheck`
2. **Run auto-analysis** (yes to all defaults)
3. **Double-click `main`** → you see decompiled C with two branches
4. **Copy the decompiled code** and paste into [claude.ai](https://claude.ai):

   > This is a decompiled binary. What does it do? Is there any way to
   > bypass the key check?

5. **Read the LLM's response** — it should find:
   - The key format: 12 chars, dashes at positions 4 and 9
   - The hash: FNV-1a (constants 2166136261 and 16777619)
   - The backdoor: a `strcmp` against a hard-coded string

6. **Prove it in the terminal:**
   ```bash
   cd lab/station3-ghidra
   ./keycheck "UIC-DEBUG-1"
   # Output: key accepted: full version unlocked
   ```

### Expected LLM response

The LLM will identify:
- **FNV-1a hash** from the two magic constants
- **Key format** `XXXX-XXXX-XX` with hash mod 1000 == 487
- **Backdoor** `UIC-DEBUG-1` that bypasses hash validation entirely

### Discussion question

> "Should this backdoor exist? Who do you tell?"
>
> The LLM finds the code — only a human makes the judgment call.

---

## Running the full demo

```bash
bash lab/demo.sh
```

This walks through both labs in the terminal with colored output and
Enter-to-advance pacing. No Ghidra needed for the terminal demo.

---

## Slides

The compiled HTML deck is included — no build step:

```bash
open slides/cs487-ai-security-teammate.html    # macOS
xdg-open slides/cs487-ai-security-teammate.html  # Linux
```

Press **f** for full-screen, **p** for presenter view.

To rebuild from source (only if you edit the Markdown):

```bash
pip install matplotlib
python3 slides/figures/make_figures.py
bash build.sh --no-pdf
```

## License

MIT. See [LICENSE](LICENSE).
