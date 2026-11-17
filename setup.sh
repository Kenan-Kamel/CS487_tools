#!/usr/bin/env bash
# ============================================================================
# CS 487 — AI for Security: One-command setup
#
# Run this to clone the repo, build the lab binaries, and open the slides.
#
#   curl -fsSL https://raw.githubusercontent.com/Kenan-Kamel/CS487_tools/main/setup.sh | bash
#
# Or if you already cloned:
#   bash setup.sh
# ============================================================================
set -euo pipefail

REPO="https://github.com/Kenan-Kamel/CS487_tools.git"
DIR="CS487_tools"

# -- Clone if needed ----------------------------------------------------------
if [ ! -d "$DIR" ]; then
    echo "Cloning $REPO ..."
    git clone "$REPO" "$DIR"
    cd "$DIR"
else
    echo "Directory $DIR already exists, pulling latest..."
    cd "$DIR"
    git pull
fi

# -- Build lab binaries -------------------------------------------------------
echo
echo "Building lab binaries..."

echo "  → keycheck"
cd lab/station3-ghidra
make 2>/dev/null || { echo "    (needs gcc)"; }
cd ../..

echo "  → heartbleed"
cd lab/station3-ghidra/heartbleed
make 2>/dev/null || { echo "    (needs gcc)"; }
python3 trigger.py 2>/dev/null || { echo "    (needs python3)"; }
cd ../../..

# -- Done ---------------------------------------------------------------------
echo
echo "============================================"
echo "  Setup complete!"
echo "============================================"
echo
echo "  Slides:  open $DIR/slides/cs487-ai-security-teammate.html in Chrome"
echo "           press f for fullscreen, p for presenter view"
echo
echo "  Demo:    bash $DIR/lab/demo.sh"
echo
echo "  No API key needed — paste decompiled code into claude.ai"
echo "============================================"

# Try to open the slides
if command -v xdg-open &>/dev/null; then
    xdg-open "$DIR/slides/cs487-ai-security-teammate.html" 2>/dev/null &
elif command -v open &>/dev/null; then
    open "$DIR/slides/cs487-ai-security-teammate.html" 2>/dev/null &
fi
