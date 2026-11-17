#!/usr/bin/env bash
# ============================================================================
# CS 487 — AI for Security: Live Demo Script
#
# Run this in a terminal during the lecture. It walks through each lab station
# step by step, pausing for you to explain and interact with an LLM.
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
prompt() { echo -e "${RED}⏎ Press Enter to continue...${RESET}"; read -r; }

# =============================================================================
banner "CS 487 · AI for Security — Live Demo"
# =============================================================================

echo -e "This demo walks through three stations:\n"
echo -e "  ${BOLD}1.${RESET} LLM vs Static Analyzers  — can an LLM out-find cppcheck?"
echo -e "  ${BOLD}2.${RESET} Heartbleed in Ghidra      — reverse a real CVE pattern"
echo -e "  ${BOLD}3.${RESET} Trigger the bugs           — see the exploits live\n"
echo -e "${DIM}No API key needed. You'll paste code into claude.ai or ChatGPT.${RESET}\n"
prompt

# =============================================================================
banner "STATION 1: LLM vs Static Analyzers"
# =============================================================================

step "Building urlparse.c..."
cd detect-with-llm
make clean 2>/dev/null || true
make 2>&1
echo

step "This is a URL parser with hidden security bugs."
info "Let's first see what traditional tools find."
echo
prompt

# -- Static analyzers ---------------------------------------------------------
step "Running gcc warnings..."
echo -e "${DIM}"
gcc -Wall -Wextra -Wformat=2 -fsyntax-only urlparse.c 2>&1 || true
echo -e "${RESET}"

if command -v flawfinder &>/dev/null; then
    step "Running flawfinder..."
    echo -e "${DIM}"
    flawfinder --minlevel=2 urlparse.c 2>&1 || true
    echo -e "${RESET}"
else
    warn "flawfinder not installed — skip (pip install flawfinder)"
fi

if command -v cppcheck &>/dev/null; then
    step "Running cppcheck..."
    echo -e "${DIM}"
    cppcheck --enable=all --suppress=missingIncludeSystem urlparse.c 2>&1 || true
    echo -e "${RESET}"
else
    warn "cppcheck not installed — skip (apt install cppcheck)"
fi

echo -e "${YELLOW}The static tools found maybe 1-2 issues (the format string, maybe strcpy).${RESET}"
echo -e "${YELLOW}Now let's ask an LLM to do the same job.${RESET}\n"
prompt

# -- LLM review ---------------------------------------------------------------
step "Copy this prompt and paste it into claude.ai or ChatGPT:"
echo
echo -e "${CYAN}┌──────────────────────────────────────────────────────────────┐${RESET}"
echo -e "${CYAN}│${RESET} Review the following C code for security vulnerabilities.    ${CYAN}│${RESET}"
echo -e "${CYAN}│${RESET} List each bug with its location, severity, and how an        ${CYAN}│${RESET}"
echo -e "${CYAN}│${RESET} attacker could exploit it.                                   ${CYAN}│${RESET}"
echo -e "${CYAN}└──────────────────────────────────────────────────────────────┘${RESET}"
echo
echo -e "${DIM}Then paste the contents of urlparse.c after the prompt.${RESET}"
echo -e "${DIM}(The file is at: $(pwd)/urlparse.c)${RESET}\n"

# Copy to clipboard if possible
if command -v xclip &>/dev/null; then
    cat urlparse.c | xclip -selection clipboard
    echo -e "${GREEN}✓ urlparse.c copied to clipboard${RESET}\n"
elif command -v xsel &>/dev/null; then
    cat urlparse.c | xsel --clipboard
    echo -e "${GREEN}✓ urlparse.c copied to clipboard${RESET}\n"
fi

echo -e "${YELLOW}Wait for the LLM response, then come back here.${RESET}\n"
prompt

# -- Reveal --------------------------------------------------------------------
step "Ground truth — how many did the LLM find?"
echo
bash reveal.sh
echo
echo -e "${BOLD}Typical results:${RESET}"
echo -e "  cppcheck/flawfinder:  ${RED}1-2 bugs${RESET}  (strcpy, maybe format string)"
echo -e "  LLM code review:      ${GREEN}4-5 bugs${RESET}  (catches semantic issues too)"
echo
prompt

# -- Exploits ------------------------------------------------------------------
step "Let's prove the bugs are real. Building with AddressSanitizer..."
make asan 2>&1
echo

step "Bug 1: strcpy buffer overflow (scheme too long)"
echo -e "${DIM}"
./urlparse-asan "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA://x/y" 2>&1 || true
echo -e "${RESET}"
prompt

step "Bug 2: format-string vulnerability (printf with user-controlled key)"
echo -e "${DIM}"
./urlparse-asan 'http://x/y?%s%s%s%s=val' 2>&1 || true
echo -e "${RESET}"
prompt

step "Bug 3: null-byte injection (%00 truncates the C string)"
echo -e "${DIM}"
./urlparse-asan 'http://x/safe%00/../etc/passwd' 2>&1 || true
echo -e "${RESET}"
info "The path looks safe, but after decoding the NUL byte hides everything after it."
echo
prompt

step "Bug 4: host buffer off-by-one (200-char hostname, no slash)"
echo -e "${DIM}"
HOST=$(python3 -c "print('A'*200)")
./urlparse-asan "http://${HOST}?x=1" 2>&1 || true
echo -e "${RESET}"
prompt

step "Bug 5: check-then-decode path traversal bypass"
echo -e "${DIM}"
./urlparse-asan 'http://x/%2e%2e/%2e%2e/etc/passwd' 2>&1 || true
echo -e "${RESET}"
info "is_safe_path() checks BEFORE url_decode() runs — %2e%2e bypasses the '..' check."
echo
prompt

cd ..

# =============================================================================
banner "STATION 2: Heartbleed in Ghidra (CVE-2014-0160 pattern)"
# =============================================================================

step "Building the Heartbleed binary (stripped)..."
cd station3-ghidra/heartbleed
make clean 2>/dev/null || true
make 2>&1
echo

step "This binary processes 'heartbeat' records — like a TLS keep-alive."
info "It has the same bug as the real Heartbleed (CVE-2014-0160):"
info "it trusts a client-specified length instead of the actual payload size."
echo
info "In a real demo, you'd import this binary into Ghidra and ask"
info "an LLM to analyze the decompiled code."
echo

step "For now, let's trigger the bug and see what leaks."
echo

step "Creating malicious heartbeat record..."
python3 trigger.py
echo

step "Sending it to the server..."
echo -e "${YELLOW}The input has 4 bytes of real payload but claims 400 bytes.${RESET}"
echo -e "${YELLOW}The memcpy reads past the buffer into the session struct.${RESET}\n"
echo -e "${BOLD}Leaked memory:${RESET}"
echo -e "${DIM}"
./heartbleed trigger.bin | xxd | head -30
echo -e "${RESET}"

echo -e "${RED}${BOLD}Look for the leaked secrets:${RESET}"
echo -e "  ${BOLD}auth_token:${RESET}  sk-prod-a7f3b2c1d4e5f609876"
echo -e "  ${BOLD}username:${RESET}    admin"
echo -e "  ${BOLD}password:${RESET}    Tr0ub4dor&3"
echo
info "In the real Heartbleed, this leaked private keys, session cookies,"
info "and passwords from ~17% of HTTPS servers on the internet."
echo
prompt

# -- Ghidra LLM prompt --------------------------------------------------------
step "If you have Ghidra open, ask the LLM:"
echo
echo -e "${CYAN}  1. \"What does this binary do? Start from main.\"${RESET}"
echo -e "${CYAN}  2. \"Describe the struct on the stack.\"${RESET}"
echo -e "${CYAN}  3. \"Find security vulnerabilities.\"${RESET}"
echo -e "${CYAN}  4. \"What data could an attacker leak?\"${RESET}"
echo
info "Or export the decompiled C from Ghidra and paste it into claude.ai."
echo

step "The fix is one line:"
echo -e "${GREEN}  if (payload_len > s->recv_len - 3) return -1;${RESET}"
info "This is exactly what the OpenSSL patch for CVE-2014-0160 added."
echo
prompt

cd ../..

# =============================================================================
banner "STATION 3: Keycheck warm-up (bonus, if time)"
# =============================================================================

step "Building the keycheck binary (stripped)..."
cd station3-ghidra
make 2>&1 || true
echo

if [ -f keycheck ]; then
    step "This checks a 12-character license key using FNV-1a hashing."
    info "It also has a backdoor: a hard-coded support key."
    echo

    step "Finding a valid key..."
    python3 findkey.py 2>&1 || true
    echo

    step "The backdoor key is:"
    echo -e "  ${RED}${BOLD}UIC-DEBUG-1${RESET}"
    echo
    echo -e "${DIM}"
    ./keycheck "UIC-DEBUG-1" 2>&1 || true
    echo -e "${RESET}"
    info "An LLM analyzing the decompiled code in Ghidra finds this in seconds."
    info "A human reverse engineer might miss it in a larger binary."
fi
echo
cd ..

# =============================================================================
banner "WRAP-UP"
# =============================================================================

echo -e "${BOLD}What we showed:${RESET}\n"
echo -e "  1. ${GREEN}LLMs catch bugs that static analyzers miss${RESET}"
echo -e "     — semantic issues like check-then-decode, null-byte injection"
echo
echo -e "  2. ${GREEN}LLMs can reverse-engineer stripped binaries${RESET}"
echo -e "     — identify algorithms, find vulnerabilities, rename symbols"
echo
echo -e "  3. ${GREEN}LLMs are not perfect${RESET}"
echo -e "     — they can hallucinate, miss context, produce false positives"
echo -e "     — always verify with real tools (ASan, Ghidra, manual review)"
echo
echo -e "${BOLD}The human decides what to trust. The LLM is a force multiplier.${RESET}\n"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Demo complete. Questions?${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
