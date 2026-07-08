---
name: image-gen-bridge
description: "AI 图片生成能力：支持文生图、图生图、多参考图、多比例输出。当用户需要生成图片、根据参考图改图、批量出图，或提到 生图、画图、AI 绘画、文生图、图生图 时使用。"
license: MIT
metadata:
  author: 78design
  version: "1.9.1"
tags:
  - image-generation
  - text-to-image
  - image-to-image
  - ai-art
  - gemini
platforms:
  - trae
  - cursor
  - claude
  - copilot
---

# image-gen-bridge Skill

AI 图片生成工具，调用 OpenAI 兼容 API，支持文生图、图生图、多张参考图、多种比例输出，内置自动 fallback 备用模型。

## When to Use This Skill

触发以下场景时使用：

- 用户要求生成图片、画图、AI 绘画
- 用户要求"文生图"或"图生图"
- 用户提供参考图并要求修改/变换风格
- 用户需要指定图片比例（如 3:4、1:1、16:9）
- 用户提到 生图、出图、画一张、生成图片 等关键词

## Not For / Boundaries

- 不做视频生成，仅处理静态图片
- 不内置模型，需要用户配置 API Key 和 API 地址
- 不对生成内容做质量审核，由用户自行判断
- 不处理版权争议素材

## Quick Reference

### 安装依赖

```bash
pip install -r scripts/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 环境变量

| 变量 | 必填 | 默认值 |
|------|------|--------|
| `IMAGE_GEN_API_KEY` | 是 | - |
| `IMAGE_GEN_API_URL` | 否 | `https://api.1openapi.com/v1` |
| `IMAGE_GEN_MODEL` | 否 | `openai/gpt-image-2` |

### 文生图

```bash
python scripts/generate.py --prompt "描述文字" --output output.png
```

### 指定比例

```bash
python scripts/generate.py --prompt "描述" --aspect-ratio "3:4" --output out.png
```

支持比例：`1:1`、`3:4`、`4:3`、`16:9`、`9:16`、`21:9`、`9:21`

### 图生图（单张参考）

```bash
python scripts/generate.py --prompt "描述" --image-file ref.jpg --output out.png
```

### 图生图（多张参考）

```bash
python scripts/generate.py --prompt "描述" --image-file a.jpg --image-file b.jpg --output out.png
```

### 指定 API 参数

```bash
python scripts/generate.py --prompt "描述" --model "google/gemini-3.1-flash-image-preview" --api-key "sk-xxx" --output out.png
```

## Configuration

| 参数 | 必需 | 说明 |
|------|------|------|
| `--prompt` | ✅ | 图片描述文字 |
| `--image-file` | ❌ | 参考图片路径，可多次指定 |
| `--output` | ❌ | 输出文件路径，默认 `generated_<时间戳>.png` |
| `--aspect-ratio` | ❌ | 图片比例，默认 `3:4` |
| `--api-url` | ❌ | 覆盖 API 地址 |
| `--api-key` | ❌ | 覆盖 API Key |
| `--model` | ❌ | 覆盖主模型 |
| `--backup-model` | ❌ | 备用模型，默认 `google/gemini-3.1-flash-image-preview` |
| `--timeout` | ❌ | 请求超时秒数，默认 `180` |
| `--help` | ❌ | 显示帮助 |

## Examples

### 示例 1：文生图 - 猫咪头像

**输入**
```bash
python scripts/generate.py --prompt "一只可爱的橘猫坐在窗台上，阳光洒进来" --aspect-ratio "1:1" --output cat.png
```

**输出**
- 生成文件 `cat.png`
- 控制台显示模型名称和保存路径

### 示例 2：图生图 - 风格变换

**输入**
```bash
python scripts/generate.py --prompt "将这张照片变成油画风格" --image-file photo.jpg --output oil_painting.png
```

**输出**
- 生成文件 `oil_painting.png`
- 参考图内容会被发送给模型作为 image_url

### 示例 3：主模型失败自动 fallback

**场景**：主模型 `openai/gpt-image-2` 负载过高

**行为**
1. 先用主模型请求
2. 失败后自动切换到备用模型 `google/gemini-3.1-flash-image-preview`
3. 控制台输出切换提示
4. 最终返回成功生成的图片

## References

- 脚本位置：`scripts/generate.py`
- 依赖列表：`scripts/requirements.txt`
- 版本号：`VERSION`
