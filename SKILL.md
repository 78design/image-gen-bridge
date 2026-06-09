---
name: image-gen-bridge
description: AI图片生成工具，支持文生图和图生图
---

# image-gen-bridge

支持文生图和图生图（支持多张参考图）。

## Usage

```bash
# Install
git clone https://github.com/78design/image-gen-bridge.git
cd image-gen-bridge
bash install.sh

# Generate
python generate.py --prompt "描述" --output image.png

# With reference image
python generate.py --prompt "描述" --image-file ref.jpg --output image.png

# Multiple references
python generate.py --prompt "描述" --image-file a.jpg --image-file b.jpg --output result.png
```

## Environment Variables

| Variable | Required | Default |
|----------|----------|--------|
| IMAGE_GEN_API_KEY | Yes | - |
| IMAGE_GEN_API_URL | No | https://api.1openapi.com/v1 |
| IMAGE_GEN_MODEL | No | openai/gpt-image-2 |

## Arguments

| Arg | Required | Description |
|-----|----------|-------------|
| --prompt | Yes | Text prompt |
| --image-file | No | Reference image (multiple allowed) |
| --output | No | Output file path |
| --api-url | No | Override API URL |
| --api-key | No | Override API key |
| --model | No | Override model |