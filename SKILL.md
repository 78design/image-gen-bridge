# image-gen-bridge

AI图片生成工具，通过OpenAI兼容接口调用各类生图模型。

支持文生图（Text-to-Image）和图生图（Image-to-Image），适用于各种OpenAI兼容的中转站/代理服务。

## Features

- Text-to-Image generation
- Image-to-Image generation (with reference image)
- Compatible with any OpenAI-compatible API endpoint
- Support for custom models (DALL-E, GPT-Image, Stable Diffusion, etc.)
- Environment variable configuration
- Automatic image URL extraction from markdown responses

## Quick Start

### 1. Clone

```bash
git clone https://github.com/78design/image-gen-bridge.git
cd image-gen-bridge
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Configure

Set your API key and endpoint:

```bash
export IMAGE_GEN_API_KEY="your-api-key"
export IMAGE_GEN_API_URL="https://your-proxy.com/v1"
export IMAGE_GEN_MODEL="your-model-name"
```

### 4. Generate

```bash
# Text-to-Image
python generate.py --prompt "A cute cat sitting on a sofa" --output cat.png

# Image-to-Image
python generate.py --prompt "A stylish woman carrying this keychain" \
  --image-file product.jpg \
  --output fashion.png
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `IMAGE_GEN_API_KEY` | Yes | - | API key for authentication |
| `IMAGE_GEN_API_URL` | No | `https://api.openai.com/v1` | API base URL |
| `IMAGE_GEN_MODEL` | No | `gpt-image-1` | Default model name |

### Command Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--prompt` | Yes | Text prompt for image generation |
| `--image-file` | No | Path to reference image (image-to-image) |
| `--output` | No | Output file path |
| `--api-url` | No | API base URL (overrides env) |
| `--api-key` | No | API key (overrides env) |
| `--model` | No | Model name (overrides env) |

Command line arguments take priority over environment variables.

## Usage Examples

### Basic Text-to-Image

```bash
python generate.py \
  --prompt "A beautiful sunset over the ocean" \
  --output sunset.png
```

### Image-to-Image with Reference

```bash
python generate.py \
  --prompt "A 22-year-old woman wearing a white crop top and jeans, carrying a bag with this plush keychain attached. Street fashion photography" \
  --image-file ./product_photo.jpg \
  --output fashion_shot.png
```

### Using Different API Providers

```bash
# Provider A
python generate.py \
  --prompt "A fantasy castle" \
  --api-url "https://provider-a.com/v1" \
  --model "dall-e-3" \
  --output castle.png

# Provider B
python generate.py \
  --prompt "A cyberpunk city" \
  --api-url "https://provider-b.com/v1" \
  --model "stable-diffusion-xl" \
  --output cyberpunk.png
```

### One-liner with Environment Variables

```bash
IMAGE_GEN_API_KEY="sk-xxx" \
IMAGE_GEN_API_URL="https://your-proxy.com/v1" \
IMAGE_GEN_MODEL="gpt-image-2" \
python generate.py --prompt "A cute dog" --output dog.png
```

## Installation Script

Run the included install script for quick setup:

```bash
bash install.sh
```

This will:
1. Install Python dependencies
2. Guide you through API configuration
3. Verify the installation

## Requirements

- Python 3.7+
- requests >= 2.31.0

## License

MIT
