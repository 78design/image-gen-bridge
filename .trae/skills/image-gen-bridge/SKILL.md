---
name: image-gen-bridge
description: AI图片生成工具，通过OpenAI兼容接口调用各类生图模型，支持文生图和图生图
---

# image-gen-bridge

当用户需要生成图片时使用此技能。支持文生图（Text-to-Image）和图生图（Image-to-Image，支持单张或多张参考图）。

## When to use

- 当用户要求生成图片时
- 当用户提到 DALL-E、Stable Diffusion、FLUX 等图像生成关键词时
- 当用户需要生成产品图、设计图、概念图等

## 内置 API Provider

安装时会提供以下内置选项供选择：

| Provider | API URL | 支持模型 |
|----------|---------|----------|
| 1OpenAPI | api.1openapi.com/v1 | openai/gpt-image-2, google/gemini-3.1-flash-image-preview |
| Custom | 用户自定义 | 用户自定义 |

## Instructions

### 1. 安装配置

让用户运行安装脚本：
```bash
cd skills/image-gen-bridge
bash install.sh
```

安装过程会引导用户：
1. 选择 API Provider（输入 1-2）
2. 选择具体模型
3. 输入 API Key

### 2. 生成图片

**文生图模式 (Text-to-Image):**
```bash
python skills/image-gen-bridge/generate.py --prompt "用户描述" --output 文件名.png
```

**图生图模式 (Image-to-Image) - 单张参考：
```bash
python skills/image-gen-bridge/generate.py --prompt "用户描述" --image-file 参考图.png --output 结果.png
```

**图生图模式 (Image-to-Image) - 多张参考：
```bash
python skills/image-gen-bridge/generate.py --prompt "用户描述" --image-file 参考图1.png --image-file 参考图2.png --output 结果.png
```

### 3. 常用参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `--prompt` | ✅ | 图片描述 |
| `--image-file` | ❌ | 参考图片路径（图生图模式，可多次使用以添加多张参考图） |
| `--output` | ❌ | 输出文件路径 |
| `--api-url` | ❌ | 覆盖 API 地址 |
| `--api-key` | ❌ | 覆盖 API Key |
| `--model` | ❌ | 覆盖模型名称 |

## Command Reference

```
python generate.py [OPTIONS]

Required:
  --prompt TEXT          Text prompt for image generation

Optional:
  --image-file PATH      Reference image for image-to-image mode (multiple allowed)
  --output PATH          Output file path
  --api-url TEXT         API base URL (overrides env)
  --api-key TEXT         API key (overrides env)
  --model TEXT           Model name (overrides env)
  --help                 Show help
```

## 环境变量

如需手动配置：
```bash
export IMAGE_GEN_API_KEY="你的API密钥"
export IMAGE_GEN_API_URL="https://api.1openapi.com/v1"
export IMAGE_GEN_MODEL="openai/gpt-image-2"
```
