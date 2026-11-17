#!/usr/bin/env bash
# ============================================================================
# CS 487 — AI for Security: One-command setup
#
# Run this to clone the repo, install Ghidra, build the lab binaries,
# and open the slides.
#
#   curl -fsSL https://raw.githubusercontent.com/Kenan-Kamel/CS487_tools/main/setup.sh | bash
#
# Or if you already cloned:
#   bash setup.sh
# ============================================================================
set -euo pipefail

REPO="https://github.com/Kenan-Kamel/CS487_tools.git"
DIR="CS487_tools"
GHIDRA_VERSION="11.3.1"
GHIDRA_DATE="20250205"
GHIDRA_ZIP="ghidra_${GHIDRA_VERSION}_PUBLIC_${GHIDRA_DATE}.zip"
GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/${GHIDRA_ZIP}"

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

# -- Install Ghidra if not found ----------------------------------------------
if command -v ghidraRun &>/dev/null || [ -d "ghidra" ] || [ -d "$HOME/ghidra" ]; then
    echo "Ghidra already installed."
else
    echo
    echo "Installing Ghidra ${GHIDRA_VERSION}..."

    # Check for Java 17+
    if ! command -v java &>/dev/null; then
        echo "  Installing Java (JDK 17)..."
        if command -v apt &>/dev/null; then
            sudo apt update -qq && sudo apt install -y -qq openjdk-17-jdk unzip wget
        elif command -v brew &>/dev/null; then
            brew install openjdk@17 unzip wget
        else
            echo "  ⚠ Please install Java 17+ manually, then re-run this script."
        fi
    fi

    echo "  Downloading Ghidra ${GHIDRA_VERSION}..."
    wget -q --show-progress -O "/tmp/${GHIDRA_ZIP}" "${GHIDRA_URL}" || {
        echo "  ⚠ Download failed. Install Ghidra manually from:"
        echo "    https://github.com/NationalSecurityAgency/ghidra/releases"
        echo "  Continuing without Ghidra..."
    }

    if [ -f "/tmp/${GHIDRA_ZIP}" ]; then
        echo "  Extracting..."
        unzip -q "/tmp/${GHIDRA_ZIP}" -d .
        mv "ghidra_${GHIDRA_VERSION}_PUBLIC" ghidra
        rm -f "/tmp/${GHIDRA_ZIP}"
        echo "  ✓ Ghidra installed at $(pwd)/ghidra"
        echo "    Run with: ./ghidra/ghidraRun"
    fi
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
echo "  Slides:   open $DIR/slides/cs487-ai-security-teammate.html"
echo "            press f for fullscreen, p for presenter view"
echo
echo "  Ghidra:   ./$DIR/ghidra/ghidraRun"
echo "            import $DIR/lab/station3-ghidra/heartbleed/heartbleed"
echo "            import $DIR/lab/station3-ghidra/keycheck"
echo
echo "  Demo:     bash $DIR/lab/demo.sh"
echo
echo "  No API key needed — paste code into claude.ai"
echo "============================================"

# Try to open the slides
if command -v xdg-open &>/dev/null; then
    xdg-open "$DIR/slides/cs487-ai-security-teammate.html" 2>/dev/null &
elif command -v open &>/dev/null; then
    open "$DIR/slides/cs487-ai-security-teammate.html" 2>/dev/null &
fi
