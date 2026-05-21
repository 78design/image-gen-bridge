#!/bin/bash
# image-gen-bridge Installer

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SHELL_RC="$HOME/.bashrc"
[ -n "$ZSH_VERSION" ] && SHELL_RC="$HOME/.zshrc"

echo "=== Installing image-gen-bridge ==="

echo "[1/3] Installing requests..."
pip install requests --break-system-packages 2>/dev/null || pip install requests
echo "Done."

echo ""
echo "[2/3] API Configuration"
echo "----------------------"

read -s -p "Enter API key: " API_KEY
echo ""
if [ -n "$API_KEY" ]; then
    grep -q "^export IMAGE_GEN_API_KEY=" "$SHELL_RC" || echo "export IMAGE_GEN_API_KEY=\"$API_KEY\"" >> "$SHELL_RC"
    export IMAGE_GEN_API_KEY="$API_KEY"
    echo "API key saved to $SHELL_RC"
fi

read -p "API URL (default: https://api.openai.com/v1): " API_URL
[ -z "$API_URL" ] && API_URL="https://api.openai.com/v1"
grep -q "^export IMAGE_GEN_API_URL=" "$SHELL_RC" || echo "export IMAGE_GEN_API_URL=\"$API_URL\"" >> "$SHELL_RC"
echo "API URL: $API_URL"

read -p "Model (default: openai/gpt-image-2): " MODEL
[ -z "$MODEL" ] && MODEL="openai/gpt-image-2"
grep -q "^export IMAGE_GEN_MODEL=" "$SHELL_RC" || echo "export IMAGE_GEN_MODEL=\"$MODEL\"" >> "$SHELL_RC"
echo "Model: $MODEL"

echo ""
echo "[3/3] Verification"
echo "------------------"
python3 "$SCRIPT_DIR/generate.py" --help > /dev/null && echo "Script: OK" || echo "Script: FAIL"
python3 -c "import requests" > /dev/null && echo "Dependencies: OK" || echo "Dependencies: FAIL"

echo ""
echo "=== Installation complete ==="
echo "Usage: python generate.py --prompt 'your prompt' --output image.png"
echo "Run: source $SHELL_RC to apply changes"