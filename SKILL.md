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

## Quick Start

### 1. 安装配置

```bash
# 克隆仓库
git clone https://github.com/78design/image-gen-bridge.git
cd image-gen-bridge

# 运行安装脚本
bash install.sh
```

安装过程会引导配置：
- API Key（必需）
- API URL（默认：https://api.openai.com/v1）
- 默认模型（默认：openai/gpt-image-2）

### 2. 生成图片

**文生图模式：**
```bash
python generate.py --prompt "一只可爱的橘猫在阳光下打盹" --output cat.png
```

**图生图模式（单张参考）：**
```bash
python generate.py --prompt "把这只猫放在沙发上" \
  --image-file cat.png --output cat_on_sofa.png
```

**图生图模式（多张参考）：**
```bash
python generate.py --prompt "结合两张图的风格" \
  --image-file style1.png --image-file style2.png \
  --output result.png
```

## 环境变量

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `IMAGE_GEN_API_KEY` | 是 | - | API 密钥 |
| `IMAGE_GEN_API_URL` | 否 | `https://api.openai.com/v1` | API 基础地址 |
| `IMAGE_GEN_MODEL` | 否 | `openai/gpt-image-2` | 默认模型名称 |

## 命令行参数

| 参数 | 必需 | 说明 |
|------|------|------|
| `--prompt` | 是 | 图片描述文本 |
| `--image-file` | 否 | 参考图片路径（可多次使用添加多张） |
| `--output` | 否 | 输出文件路径 |
| `--api-url` | 否 | API 地址（覆盖环境变量） |
| `--api-key` | 否 | API 密钥（覆盖环境变量） |
| `--model` | 否 | 模型名称（覆盖环境变量） |

命令行参数优先于环境变量。

## 使用示例

### 基础文生图

```bash
python generate.py \
  --prompt "美丽的海上日落" \
  --output sunset.png
```

### 单参考图生图

```bash
python generate.py \
  --prompt "一个年轻女性穿着白色背心和牛仔裤，背着带有这个钥匙扣的包包，街头时尚摄影" \
  --image-file ./product_photo.jpg \
  --output fashion_shot.png
```

### 多参考图生图

```bash
python generate.py \
  --prompt "结合photo1的光线和photo2的构图创建产品照片" \
  --image-file ./photo1.jpg --image-file ./photo2.jpg \
  --output combined_product.png
```

### 使用不同 API 提供商

```bash
# 提供商 A
python generate.py \
  --prompt "一座幻想城堡" \
  --api-url "https://provider-a.com/v1" \
  --model "dall-e-3" \
  --output castle.png

# 提供商 B
python generate.py \
  --prompt "一座赛博朋克城市" \
  --api-url "https://provider-b.com/v1" \
  --model "stable-diffusion-xl" \
  --output cyberpunk.png
```

### 一行命令配置

```bash
IMAGE_GEN_API_KEY="sk-xxx" \
IMAGE_GEN_API_URL="https://your-proxy.com/v1" \
IMAGE_GEN_MODEL="gpt-image-2" \
python generate.py --prompt "一只可爱的狗" --output dog.png
```

## 安装脚本

运行附带的安装脚本快速配置：

```bash
bash install.sh
```

这将：
1. 安装 Python 依赖（requests 库）
2. 引导配置 API 密钥和参数
3. 验证安装
4. 测试 API 连接

## 常见问题

### Q: 安装后提示找不到命令？

运行以下命令重新加载配置：
```bash
source ~/.bashrc  # 或 ~/.zshrc
```

### Q: 如何更新 API 配置？

编辑 `~/.bashrc`（或 `~/.zshrc`），修改对应的 export 行：
```bash
export IMAGE_GEN_API_KEY="your-new-key"
export IMAGE_GEN_API_URL="https://new-provider.com/v1"
export IMAGE_GEN_MODEL="new-model"
```

### Q: 支持哪些图片格式？

支持 `.jpg`、`.jpeg`、`.png` 格式作为参考图。

### Q: API 请求超时怎么办？

可以设置更长的超时时间，但建议检查网络连接和 API 服务状态。

### Q: 如何查看详细错误信息？

添加 `--verbose` 参数（如支持）或检查 API 返回的错误信息。

## 系统要求

- Python 3.7+
- requests >= 2.31.0
- 网络连接（访问 API 服务）