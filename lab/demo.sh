#!/usr/bin/env bash
# ============================================================================
# CS 487 — AI for Security: Live Demo Script
#
# Run this in a terminal during the lecture. Two stations, Enter to advance.
#
# No API key required. When the script says "paste into an LLM", open
# claude.ai (free), ChatGPT, or any chat interface.
#
# Usage:  bash lab/demo.sh
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")"

# -- Colors and helpers -------------------------------------------------------
RED='\033[1;31m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

banner() { echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"; echo -e "${BOLD}  $1${RESET}"; echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"; }
step()   { echo -e "${GREEN}▶ $1${RESET}"; }
info()   { echo -e "${DIM}  $1${RESET}"; }
warn()   { echo -e "${YELLOW}⚠ $1${RESET}"; }
prompt() { echo -e "\n${RED}⏎ Press Enter to continue...${RESET}"; read -r; }

# =============================================================================
banner "CS 487 · AI for Security — Live Demo"
# =============================================================================

echo -e "Two stations:\n"
echo -e "  ${BOLD}1.${RESET} Heartbleed (CVE-2014-0160) — reverse-engineer a real vulnerability in Ghidra"
echo -e "  ${BOLD}2.${RESET} Keycheck backdoor          — find a hidden key in a stripped binary\n"
echo -e "${DIM}No API key needed. Paste decompiled code into claude.ai or ChatGPT.${RESET}"
prompt

# =============================================================================
banner "STATION 1: Heartbleed (CVE-2014-0160 pattern)"
# =============================================================================

step "Background: what was Heartbleed?"
echo
echo -e "  In April 2014, a bug in OpenSSL's TLS heartbeat handler let any"
echo -e "  client read up to 64 KB of server memory per request — private keys,"
echo -e "  passwords, session tokens. ${BOLD}~17% of all HTTPS servers were affected.${RESET}"
echo
echo -e "  The bug: the server trusted a ${RED}client-specified payload length${RESET}"
echo -e "  instead of checking how many bytes were actually received."
prompt

# -- Build --------------------------------------------------------------------
step "Building the Heartbleed binary (stripped, no debug symbols)..."
cd station3-ghidra/heartbleed
make clean 2>/dev/null || true
make 2>&1
echo
info "The binary is stripped — no function names, no variable names."
info "This is what a real attacker or analyst starts with."
prompt

# -- Explain the protocol -----------------------------------------------------
step "How the heartbeat protocol works:"
echo
echo -e "  Client sends:   ${CYAN}[type: 1 byte] [length: 2 bytes] [payload: N bytes]${RESET}"
echo -e "  Server echoes:   ${CYAN}[type: 1 byte] [length: 2 bytes] [payload: N bytes]${RESET}"
echo
echo -e "  The ${RED}bug${RESET}: the server copies ${RED}length${RESET} bytes from memory,"
echo -e "  not the actual number of bytes received."
echo
echo -e "  If the client sends 4 bytes of payload but claims length = 400,"
echo -e "  the server copies 396 extra bytes from adjacent memory."
prompt

# -- Trigger the bug ----------------------------------------------------------
step "Creating a malicious heartbeat request..."
python3 trigger.py
echo
echo -e "  Real payload:    ${GREEN}4 bytes${RESET} (\"PING\")"
echo -e "  Claimed length:  ${RED}400 bytes${RESET}"
prompt

step "Sending it to the server..."
echo -e "${BOLD}Leaked memory (hex dump):${RESET}\n"
./heartbleed trigger.bin | xxd | head -30
echo

echo -e "${RED}${BOLD}Secrets visible in the dump:${RESET}"
echo -e "  offset 0x104:  ${BOLD}sk-prod-a7f3b2c1d4e5f609876${RESET}   ← auth token"
echo -e "  offset 0x144:  ${BOLD}admin${RESET}                          ← username"
echo -e "  offset 0x164:  ${BOLD}Tr0ub4dor&3${RESET}                    ← password"
echo
info "In the real Heartbleed, attackers extracted private SSL keys this way."
prompt

# -- Ghidra + LLM analysis ----------------------------------------------------
step "Now: reverse-engineer this binary with Ghidra + an LLM"
echo
echo -e "  ${BOLD}Option A — Ghidra + GhidraMCP + Claude Code:${RESET}"
echo -e "  Import ./heartbleed into Ghidra, run auto-analysis."
echo -e "  Then ask Claude Code to analyze it via MCP.\n"
echo -e "  ${BOLD}Option B — Ghidra + paste into claude.ai (no API key):${RESET}"
echo -e "  Import ./heartbleed into Ghidra, run auto-analysis."
echo -e "  File → Export Program → C/C++ to get decompiled source."
echo -e "  Paste it into claude.ai with this prompt:\n"
echo -e "${CYAN}┌──────────────────────────────────────────────────────────────┐${RESET}"
echo -e "${CYAN}│${RESET} This is decompiled C from a stripped binary. Find all        ${CYAN}│${RESET}"
echo -e "${CYAN}│${RESET} security vulnerabilities. For each one, explain the bug,     ${CYAN}│${RESET}"
echo -e "${CYAN}│${RESET} how to exploit it, and how to fix it.                        ${CYAN}│${RESET}"
echo -e "${CYAN}└──────────────────────────────────────────────────────────────┘${RESET}"
echo
info "The LLM should identify:"
info "  • The struct layout (buffer + secrets in adjacent memory)"
info "  • The missing bounds check on memcpy"
info "  • That the client-controlled length leaks memory"
info "  • The connection to CVE-2014-0160"
prompt

step "The fix is one line:"
echo
echo -e "  ${GREEN}if (payload_len > s->recv_len - 3) return -1;${RESET}"
echo
info "This is exactly what the OpenSSL patch for CVE-2014-0160 added."
info "The LLM finds this in seconds. The original bug went undetected for 2 years."
prompt

cd ../..

# =============================================================================
banner "STATION 2: Keycheck — finding a backdoor"
# =============================================================================

step "Building the keycheck binary (stripped)..."
cd station3-ghidra
make 2>&1 || true
echo

if [ ! -f keycheck ]; then
    warn "keycheck binary not found — skipping this station."
    cd ..
else
    step "This program checks a 12-character license key."
    info "Format: XXXX-XXXX-XX, validated with an FNV-1a hash."
    echo
    echo -e "  ${DIM}$ ./keycheck AAAA-BBBB-CC${RESET}"
    echo -e "  invalid key"
    echo
    ./keycheck "AAAA-BBBB-CC" 2>&1 || true
    prompt

    step "Finding a valid key by brute force..."
    python3 findkey.py 2>&1 || true
    prompt

    step "But there's also a backdoor — a hard-coded support key."
    echo
    echo -e "  ${RED}${BOLD}UIC-DEBUG-1${RESET}"
    echo
    ./keycheck "UIC-DEBUG-1" 2>&1 || true
    echo
    info "In Ghidra, the LLM finds this by spotting a strcmp() against a string"
    info "constant on a separate code path from the hash check."
    echo
    info "Ask the class: should this backdoor exist? Who do you tell?"
    info "The model finds the code — the human makes the judgment call."
    prompt

    cd ..
fi

# =============================================================================
banner "TAKEAWAYS"
# =============================================================================

echo -e "${BOLD}What we showed today:${RESET}\n"
echo -e "  ${GREEN}1.${RESET} LLMs can reverse-engineer stripped binaries"
echo -e "     Identify algorithms, find vulnerabilities, rename symbols"
echo
echo -e "  ${GREEN}2.${RESET} LLMs find bugs that went undetected for years"
echo -e "     Heartbleed was live for 2 years before a human found it"
echo
echo -e "  ${GREEN}3.${RESET} LLMs spot hidden backdoors"
echo -e "     But they cannot tell you if a backdoor is authorized"
echo
echo -e "  ${RED}⚠${RESET}  LLMs are not a replacement for verification"
echo -e "     Always confirm with real tools: ASan, fuzzing, manual review"
echo
echo -e "  ${BOLD}The human decides what to trust. The LLM is a force multiplier.${RESET}\n"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Demo complete. Questions?${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
