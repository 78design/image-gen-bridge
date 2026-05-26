#!/bin/bash
# image-gen-bridge - Installation Script

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SHELL_RC=""

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

echo "[1/3] Installing Python dependencies..."

# Try pip3 first, fallback to pip
PIP_CMD="pip3"
if ! command -v $PIP_CMD &> /dev/null; then
    PIP_CMD="pip"
fi

echo "   Using: $PIP_CMD"

install_deps() {
    if [ -n "$VIRTUAL_ENV" ] || [ -f "pyproject.toml" ] || [ -f "Pipfile" ]; then
        $PIP_CMD install -r "$SCRIPT_DIR/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
    else
        $PIP_CMD install -r "$SCRIPT_DIR/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/ --break-system-packages 2>/dev/null || \
            $PIP_CMD install -r "$SCRIPT_DIR/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
    fi
}

if ! install_deps; then
    echo ""
    echo "Warning: Failed to install dependencies with default mirror."
    echo "         Trying without mirror..."
    echo ""
    if ! $PIP_CMD install -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null; then
        echo ""
        echo "Error: Failed to install dependencies."
        echo ""
        echo "Please install manually using one of these commands:"
        echo "  pip3 install -r $SCRIPT_DIR/requirements.txt"
        echo "  or"
        echo "  pip install -r $SCRIPT_DIR/requirements.txt"
        echo ""
        exit 1
    fi
fi

echo "   Done."
echo ""

echo "[2/3] API Configuration"
echo "-----------------------------------------"

declare -A PROVIDERS
PROVIDERS[1]="1OpenAPI|https://api.1openapi.com/v1|openai/gpt-image-2"
PROVIDERS[2]="Custom API|custom|custom"

declare -A MODELS_1OPENAPI
MODELS_1OPENAPI[1]="openai/gpt-image-2"
MODELS_1OPENAPI[2]="google/gemini-3.1-flash-image-preview"

echo "Select API Provider:"
echo "  1) 1OpenAPI (推荐)"
echo "  2) Custom API"
echo ""
read -p "Enter choice (1-2) [1]: " PROVIDER_CHOICE
PROVIDER_CHOICE=${PROVIDER_CHOICE:-1}

IFS='|' read -r SELECTED_NAME SELECTED_URL SELECTED_MODEL <<< "${PROVIDERS[$PROVIDER_CHOICE]}"

if [ "$SELECTED_URL" = "custom" ]; then
    echo ""
    echo "Enter your custom API base URL:"
    read -r SELECTED_URL
    SELECTED_URL="${SELECTED_URL%/}"
    if [ ! -n "$SELECTED_URL" ]; then
        echo "Error: API URL is required"
        exit 1
    fi
    
    echo ""
    echo "Enter model name:"
    read -r SELECTED_MODEL
    if [ ! -n "$SELECTED_MODEL" ]; then
        echo "Error: Model name is required"
        exit 1
    fi
    SELECTED_NAME="Custom"
else
    echo ""
    echo "Selected: $SELECTED_NAME"
    echo ""
    echo "Select Model:"
    echo "  1) openai/gpt-image-2"
    echo "  2) google/gemini-3.1-flash-image-preview"
    echo ""
    read -p "Enter choice (1-2) [1]: " MODEL_CHOICE
    MODEL_CHOICE=${MODEL_CHOICE:-1}
    SELECTED_MODEL="${MODELS_1OPENAPI[$MODEL_CHOICE]}"
fi

echo ""
echo "Configuration Summary:"
echo "  Provider: $SELECTED_NAME"
echo "  API URL:  $SELECTED_URL"
echo "  Model:    $SELECTED_MODEL"
echo ""

echo "Enter your API Key:"
read -r -s API_KEY_INPUT
echo ""

if [ ! -n "$API_KEY_INPUT" ]; then
    echo "Error: API Key is required"
    exit 1
fi

save_config() {
    local var="$1"
    local value="$2"
    if ! grep -q "$var" "$SHELL_RC" 2>/dev/null; then
        echo "export $var=\"$value\"" >> "$SHELL_RC"
    fi
}

save_config "IMAGE_GEN_API_KEY" "$API_KEY_INPUT"
save_config "IMAGE_GEN_API_URL" "$SELECTED_URL"
save_config "IMAGE_GEN_MODEL" "$SELECTED_MODEL"

echo "   API Key: saved to $SHELL_RC"
echo "   API URL: saved to $SHELL_RC"
echo "   Model: saved to $SHELL_RC"
echo ""

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
echo "Next steps:"
echo "  1. Restart your terminal or run: source $SHELL_RC"
echo "  2. Generate your first image:"
echo "     python $SCRIPT_DIR/generate.py --prompt \"A cute cat\" --output cat.png"
echo ""
