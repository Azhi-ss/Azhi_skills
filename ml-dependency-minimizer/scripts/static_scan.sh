#!/usr/bin/env bash
# ==============================================================================
# Static Dependency Scanner — Wrapper around pipreqs
#
# Usage:
#   ./static_scan.sh /path/to/project
#   ./static_scan.sh /path/to/project --save /tmp/static_deps.txt
# ==============================================================================

set -euo pipefail

PROJECT_DIR="${1:-.}"
SAVE_FLAG="${2:-}"
SAVE_PATH="${3:-}"

# Ensure pipreqs is installed
if ! command -v pipreqs &> /dev/null; then
    echo "[INFO] pipreqs not found, installing..."
    pip install pipreqs --index-url https://pypi.org/simple/ -q
fi

echo "============================================"
echo "Static Dependency Scanner"
echo "============================================"
echo "Scanning: $(realpath "$PROJECT_DIR")"
echo ""

if [ "$SAVE_FLAG" = "--save" ] && [ -n "$SAVE_PATH" ]; then
    echo "[INFO] Saving results to: $SAVE_PATH"
    pipreqs "$PROJECT_DIR" --savepath "$SAVE_PATH" --force
    echo ""
    echo "Results:"
    cat "$SAVE_PATH"
else
    echo "[INFO] Dry run (print only):"
    echo ""
    pipreqs "$PROJECT_DIR" --print
fi

echo ""
echo "============================================"
echo "NOTE: Static analysis may miss:"
echo "  - Dynamic imports (importlib, __import__)"
echo "  - Conditional imports (if/else branches)"
echo "  - Framework plugin dependencies"
echo "  - Git-hosted packages"
echo ""
echo "Run dynamic_probe.py to catch these."
echo "============================================"
