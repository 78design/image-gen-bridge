#!/bin/bash
# image-gen-bridge - Installation Script

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SHELL_RC=""

# Detect shell config file
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

echo ""
echo "========================================="
echo "  image-gen-bridge - Installer"
echo "========================================="
echo ""

# Step 1: Install dependencies
echo "[1/3] Installing Python dependencies..."

# Detect virtual environment to avoid --break-system-packages warnings
if [ -n "$VIRTUAL_ENV" ] || [ -f "pyproject.toml" ] || [ -f "Pipfile" ]; then
    pip install requests 2>/dev/null || {
        echo "Error: Failed to install dependencies."
        echo "Please run manually: pip install requests"
        exit 1
    }
else
    pip install requests --break-system-packages 2>/dev/null || {
        echo "Error: Failed to install dependencies."
        echo "Please run manually: pip install requests"
        exit 1
    }
fi
echo "   Done."
echo ""

# Step 2: Configure API
echo "[2/3] API Configuration"
echo "------------------------"

# Check if already configured
if [ -n "$IMAGE_GEN_API_KEY" ]; then
    echo "   IMAGE_GEN_API_KEY: already set"
else
    echo "   Enter your API key:"
    read -r -s API_KEY_INPUT
    echo ""
    if [ -n "$API_KEY_INPUT" ]; then
        if ! grep -q "IMAGE_GEN_API_KEY" "$SHELL_RC" 2>/dev/null; then
            echo "export IMAGE_GEN_API_KEY=\"$API_KEY_INPUT\"" >> "$SHELL_RC"
            export IMAGE_GEN_API_KEY="$API_KEY_INPUT"
            echo "   IMAGE_GEN_API_KEY: saved to $SHELL_RC"
        else
            echo "   IMAGE_GEN_API_KEY: already exists in $SHELL_RC, skipping"
        fi
    else
        echo "   Skipped (you can set it later)"
    fi
fi

if [ -n "$IMAGE_GEN_API_URL" ]; then
    echo "   IMAGE_GEN_API_URL: $IMAGE_GEN_API_URL"
else
    echo ""
    echo "   Enter your API base URL (press Enter for default: https://api.openai.com/v1):"
    read -r API_URL_INPUT
    if [ -n "$API_URL_INPUT" ]; then
        if ! grep -q "IMAGE_GEN_API_URL" "$SHELL_RC" 2>/dev/null; then
            echo "export IMAGE_GEN_API_URL=\"$API_URL_INPUT\"" >> "$SHELL_RC"
            export IMAGE_GEN_API_URL="$API_URL_INPUT"
            echo "   IMAGE_GEN_API_URL: saved to $SHELL_RC"
        else
            echo "   IMAGE_GEN_API_URL: already exists in $SHELL_RC, skipping"
        fi
    else
        echo "   Using default: https://api.openai.com/v1"
    fi
fi

if [ -n "$IMAGE_GEN_MODEL" ]; then
    echo "   IMAGE_GEN_MODEL: $IMAGE_GEN_MODEL"
else
    echo ""
    echo "   Enter default model name (press Enter for default: openai/gpt-image-2):"
    read -r MODEL_INPUT
    if [ -n "$MODEL_INPUT" ]; then
        if ! grep -q "IMAGE_GEN_MODEL" "$SHELL_RC" 2>/dev/null; then
            echo "export IMAGE_GEN_MODEL=\"$MODEL_INPUT\"" >> "$SHELL_RC"
            export IMAGE_GEN_MODEL="$MODEL_INPUT"
            echo "   IMAGE_GEN_MODEL: saved to $SHELL_RC"
        else
            echo "   IMAGE_GEN_MODEL: already exists in $SHELL_RC, skipping"
        fi
    else
        echo "   Using default: openai/gpt-image-2"
    fi
fi

echo ""

# Step 3: Verify
echo "[3/3] Verifying installation..."
python3 "$SCRIPT_DIR/generate.py" --help > /dev/null 2>&1 && \
    echo "   Script: OK" || \
    echo "   Script: FAILED"

python3 -c "import requests" 2>/dev/null && \
    echo "   Dependencies: OK" || \
    echo "   Dependencies: FAILED"

echo ""
echo "========================================="
echo "  Installation complete!"
echo "========================================="
echo ""
echo "Usage:"
echo "  python generate.py --prompt \"your prompt\" --output image.png"
echo ""
echo "With reference image:"
echo "  python generate.py --prompt \"your prompt\" --image-file ref.jpg --output image.png"
echo ""
echo "Config file: $SHELL_RC"
echo ""