#!/usr/bin/env bash
# Run static analyzers on urlparse.c and collect findings.
set -euo pipefail

SRC=urlparse.c

echo "===== gcc -Wall -Wextra -Wformat=2 ====="
gcc -Wall -Wextra -Wformat=2 -fsyntax-only "$SRC" 2>&1 || true
echo

if command -v flawfinder &>/dev/null; then
    echo "===== flawfinder ====="
    flawfinder --minlevel=1 "$SRC" 2>&1 || true
    echo
fi

if command -v cppcheck &>/dev/null; then
    echo "===== cppcheck ====="
    cppcheck --enable=all --suppress=missingIncludeSystem "$SRC" 2>&1 || true
    echo
fi

echo "===== Done ====="
echo "Now ask an LLM to review urlparse.c and compare the findings."
