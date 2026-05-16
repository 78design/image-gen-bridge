# 🖼️ image-gen-bridge

AI图片生成工具，支持文生图和图生图。

## 🚀 一键安装

在终端运行：

```bash
npx skilldirs add 78design/image-gen-bridge --yes --copy
```

> ✅ 支持所有主流 AI Agent：Trae、Cursor、Claude Code、OpenCode 等

安装后进入目录配置：

```bash
cd skills/image-gen-bridge
bash install.sh
```

按照提示选择 API Provider，输入 API Key 即可。

## 📸 使用方法

```bash
# 文生图
python skills/image-gen-bridge/generate.py --prompt "一只可爱的猫咪" --output cat.png

# 图生图（参考图）
python skills/image-gen-bridge/generate.py --prompt "把这只猫放在沙发上" --image-file cat.png --output cat_on_sofa.png
```

## ⚙️ 内置 API Provider

| Provider | API 地址 | 模型 |
|----------|-----------|------|
| 1OpenAPI ⭐ | api.1openapi.com/v1 | openai/gpt-image-2, google/gemini-3.1-flash-image-preview |
| Custom | 自定义 | 自定义 |

## 🔧 手动配置

如果不用安装向导，可以手动设置环境变量：

```bash
export IMAGE_GEN_API_KEY="你的API密钥"
export IMAGE_GEN_API_URL="https://api.1openapi.com/v1"
export IMAGE_GEN_MODEL="openai/gpt-image-2"
```

## 📦 获取 API Key

推荐使用 [1OpenAPI](https://www.1openapi.com)，性价比高，支持 GPT Image 模型。

## License

MIT
