# 🖼️ image-gen-bridge

AI图片生成工具，支持文生图和图生图。

## 📦 当前版本

v1.4.0

## 🚀 安装方法

### 方法一：使用 skilldirs 一键安装（推荐）

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

---

### 方法二：Git 克隆安装

```bash
# 克隆仓库
git clone https://github.com/78design/image-gen-bridge.git
cd image-gen-bridge

# 安装配置
bash install.sh
```

---

### 方法三：下载压缩包安装

**点击直接下载：[image-gen-bridge-v1.4.0.zip](https://github.com/78design/image-gen-bridge/releases/download/v1.4.0/image-gen-bridge-v1.4.0.zip)**

或从 [GitHub Releases](https://github.com/78design/image-gen-bridge/releases/tag/v1.4.0) 页面下载：

```bash
# 解压
unzip image-gen-bridge-v1.4.0.zip
cd image-gen-bridge

# 安装配置
bash install.sh
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

### 多图生成
```bash
# 生成 4 张图片
python generate.py --prompt "一只可爱的猫咪" --number 4 --output cat.png
```

### 图生图（单张参考图）
```bash
python generate.py --prompt "把这只猫放在沙发上" --image-file cat.png --output cat_on_sofa.png
```

### 图生图（多张参考图）
```bash
python generate.py --prompt "结合两张参考图的风格" --image-file style1.png --image-file style2.png --output result.png
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

## 📖 完整参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--prompt` | ✅ | 图片描述 |
| `--image-file` | ❌ | 参考图片路径（可多次使用） |
| `--output` | ❌ | 输出文件路径 |
| `--number` | ❌ | 生成图片数量（默认 1） |
| `--aspect-ratio` | ❌ | 图片比例（默认 3:4，支持 1:1, 16:9, 9:16 等） |
| `--api-url` | ❌ | 覆盖 API 地址 |
| `--api-key` | ❌ | 覆盖 API Key |
| `--model` | ❌ | 覆盖模型名称 |
| `--help` | ❌ | 显示帮助 |

## 🔄 更新日志

### v1.4.0
- 🔧 修复：`--aspect-ratio` 参数实现方式，从无效的 `size` payload 改为拼入 prompt 文本
- 🔧 优化：默认 API 地址统一为 `https://api.1openapi.com/v1`
- 🔧 优化：默认模型统一为 `openai/gpt-image-2`

### v1.3.0
- ✨ 新增：GitHub Actions 自动化发布流程
- ✨ 新增：release.sh 一键版本发布脚本
- 🔧 优化：压缩包生成流程集成到 CI

### v1.2.0
- ✨ 新增：支持多图生成（`--number` 参数）
- ✨ 新增：支持图片比例参数（`--aspect-ratio`，默认 3:4）
- 🔧 优化：安装脚本更健壮（支持 pip3、阿里云镜像、自动重试）

### v1.1.0
- ✨ 新增：支持多图生成（`--number` 参数）
- ✨ 新增：API Key 格式预检查
- ✨ 新增：运行进度提示
- ✨ 新增：VERSION 版本管理文件
- ✨ 新增：支持图片比例参数（`--aspect-ratio`）
- 🔧 优化：安装脚本更健壮（支持 pip3、阿里云镜像、自动重试）
- 🔧 优化：添加 UTF-8 编码声明
- 🔧 优化：修复 OpenSSL 兼容警告
- 🔧 优化：优化依赖管理

### v1.0.0
- 🎉 初始版本发布

## License

MIT
