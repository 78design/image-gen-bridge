# image-gen-bridge

AI 图片生成工具，支持文生图和图生图。

## 📦 当前版本

v1.8.6

## 🚀 安装方法

### 方法一：使用 skilldirs 一键安装（推荐）

```bash
npx skilldirs add 78design/image-gen-bridge --yes --copy
```

> ✅ 支持所有主流 AI Agent：Trae、Cursor、Claude Code、OpenCode 等

### 方法二：Git 克隆

```bash
git clone https://github.com/78design/image-gen-bridge.git
cd image-gen-bridge
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 方法三：下载压缩包

[GitHub Releases v1.8.6](https://github.com/78design/image-gen-bridge/releases/tag/v1.8.6) 页面下载 `image-gen-bridge-v1.8.6.zip`，解压后：

```bash
cd image-gen-bridge
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 🔧 手动配置

设置环境变量：

```bash
export IMAGE_GEN_API_KEY="你的API密钥"
export IMAGE_GEN_API_URL="https://api.1openapi.com/v1"
export IMAGE_GEN_MODEL="openai/gpt-image-2"
```

## 📸 使用方法

### 文生图

```bash
python generate.py --prompt "一只可爱的猫咪" --output cat.png
```

### 指定比例

```bash
# 3:4 竖版（默认）
python generate.py --prompt "一只可爱的猫咪" --aspect-ratio "3:4" --output cat.png

# 1:1 方形
python generate.py --prompt "一只可爱的猫咪" --aspect-ratio "1:1" --output cat.png

# 16:9 横版
python generate.py --prompt "一只可爱的猫咪" --aspect-ratio "16:9" --output cat.png
```

### 图生图

```bash
# 单张参考图
python generate.py --prompt "把这只猫放在沙发上" --image-file cat.png --output result.png

# 多张参考图
python generate.py --prompt "结合两张参考图的风格" --image-file style1.png --image-file style2.png --output result.png
```

## ⚙️ 内置 API Provider

| Provider | API 地址 | 模型 |
|----------|-----------|------|
| 1OpenAPI ⭐ | api.1openapi.com/v1 | openai/gpt-image-2, google/gemini-3.1-flash-image-preview |
| Custom | 自定义 | 自定义 |

## 📖 完整参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--prompt` | ✅ | 图片描述 |
| `--image-file` | ❌ | 参考图片路径（可多次使用） |
| `--output` | ❌ | 输出文件路径 |
| `--aspect-ratio` | ❌ | 图片比例（默认 3:4，支持 1:1, 16:9, 9:16 等） |
| `--api-url` | ❌ | 覆盖 API 地址 |
| `--api-key` | ❌ | 覆盖 API Key |
| `--model` | ❌ | 覆盖模型名称 |
| `--backup-model` | ❌ | 备用模型（默认 google/gemini-3.1-flash-image-preview） |
| `--timeout` | ❌ | 请求超时时间（默认 180s） |
| `--help` | ❌ | 显示帮助 |

## 🔄 更新日志

### v1.8.6
- 🔧 重构：仓库目录结构，移除 `.trae/` 子目录
- 🔧 重构：移除 `install.sh`，统一使用 `npx skilldirs` 一键安装
- ✨ 新增：`build.sh` 脚本，一键构建发布压缩包

### v1.8.5
- 🔧 优化：备用模型改为 `google/gemini-3.1-flash-image-preview`（支持比例参数）
- 🔧 移除：裁剪代码（Gemini 3.1 已能正确生成目标比例）
- ✨ 新增：输出显示使用的模型名称

## License

MIT
