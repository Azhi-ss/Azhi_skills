#!/usr/bin/env bash
# ==============================================================================
# Clean Environment Validation Script
#
# Creates a fresh venv, installs only the specified requirements, and attempts
# to import the target module. Iterates until all imports succeed.
#
# Usage:
#   ./validate_clean_env.sh /path/to/requirements.txt "mypackage.main"
#   ./validate_clean_env.sh requirements.txt "mypackage.train" --cpu-torch
# ==============================================================================

set -euo pipefail

REQUIREMENTS="${1:?Usage: $0 <requirements.txt> <import_target> [--cpu-torch]}"
TARGET="${2:?Usage: $0 <requirements.txt> <import_target> [--cpu-torch]}"
CPU_TORCH="${3:-}"

VENV_DIR="/tmp/dep_validation_env_$$"

echo "============================================"
echo "Clean Environment Validator"
echo "============================================"
echo "Requirements : $REQUIREMENTS"
echo "Import target: $TARGET"
echo "Venv location: $VENV_DIR"
echo ""

# Create clean venv
echo "[1/4] Creating clean virtual environment..."
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install CPU torch if requested
if [ "$CPU_TORCH" = "--cpu-torch" ]; then
    echo "[2/4] Installing CPU-only PyTorch..."
    pip install torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cpu -q
else
    echo "[2/4] Skipping CPU torch (use --cpu-torch to enable)"
fi

# Install requirements
echo "[3/4] Installing requirements..."
pip install -r "$REQUIREMENTS" -q

# Test import
echo "[4/4] Testing import: $TARGET"
echo ""

if python -c "import $TARGET; print('✅ Import successful: $TARGET')"; then
    echo ""
    echo "============================================"
    echo "✅ VALIDATION PASSED"
    echo "All dependencies are satisfied."
    echo "============================================"
    EXIT_CODE=0
else
    echo ""
    echo "============================================"
    echo "❌ VALIDATION FAILED"
    echo "The import above failed. Check the error"
    echo "message and add the missing package to"
    echo "your requirements.txt, then re-run."
    echo "============================================"
    EXIT_CODE=1
fi

# Cleanup
deactivate 2>/dev/null || true
rm -rf "$VENV_DIR"

exit $EXIT_CODE
