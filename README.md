# image-gen-bridge

AI 图片生成工具，支持文生图和图生图。符合 SKILL.md 规范的标准技能包。

## 📦 当前版本

v1.9.2

## 🚀 安装

```bash
npx skilldirs add 78design/image-gen-bridge --yes --copy
```

安装完成后，进入技能目录安装 Python 依赖：

```bash
pip install -r scripts/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

> ✅ 支持 Trae、Cursor、Claude Code、OpenCode 等所有主流 AI Agent
> 💡 macOS/Linux 若遇到 PEP 668 限制，加 `--break-system-packages` 参数

## 🔧 配置

设置环境变量：

```bash
export IMAGE_GEN_API_KEY="你的API密钥"
export IMAGE_GEN_API_URL="https://api.1openapi.com/v1"
export IMAGE_GEN_MODEL="openai/gpt-image-2"
```

## 📸 使用方法

### 文生图

```bash
python scripts/generate.py --prompt "一只可爱的猫咪" --output cat.png
```

### 指定比例

```bash
python scripts/generate.py --prompt "一只可爱的猫咪" --aspect-ratio "3:4" --output cat.png
```

支持比例：`1:1`、`3:4`、`4:3`、`16:9`、`9:16`、`21:9`、`9:21`

### 图生图

**本地文件：**
```bash
python scripts/generate.py --prompt "把这只猫放在沙发上" --image-file cat.png --output result.png
```

**URL 链接：**
```bash
python scripts/generate.py --prompt "把这只猫变成卡通风格" --image-file "https://example.com/cat.jpg" --output result.png
```

### 多张参考图

本地文件和 URL 可混用：
```bash
python scripts/generate.py --prompt "结合两张参考图" --image-file a.jpg --image-file "https://example.com/b.png" --output result.png
```

## 📂 目录结构

```
image-gen-bridge/
├── SKILL.md              # 技能说明（AI Agent 读取）
├── README.md             # 人类可读说明
├── LICENSE               # MIT 许可证
├── VERSION               # 版本号
├── scripts/
│   ├── generate.py       # 核心生成脚本
│   └── requirements.txt  # Python 依赖
├── build.sh              # 构建发布包
└── release.sh            # 版本发布脚本
```

## ⚙️ 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--prompt` | ✅ | 图片描述 |
| `--image-file` | ❌ | 参考图片（支持本地路径或 http/https URL，可多次使用） |
| `--output` | ❌ | 输出文件路径 |
| `--aspect-ratio` | ❌ | 图片比例（默认 3:4） |
| `--api-url` | ❌ | 覆盖 API 地址 |
| `--api-key` | ❌ | 覆盖 API Key |
| `--model` | ❌ | 覆盖模型名称 |
| `--backup-model` | ❌ | 备用模型（默认 google/gemini-3.1-flash-image-preview） |

## 🔄 更新日志

### v1.9.2
- ✨ 新增：--image-file 参数支持 http/https URL 链接作为参考图
- ✨ 支持本地文件和 URL 混用（多参考图场景）
- 🔧 优化：依赖缺失时自动输出 requirements.txt 的绝对路径

### v1.9.1
- 🔧 核心优化：移除请求超时限制（timeout=None）
- 🔧 核心优化：删除内部重试逻辑，接口返回什么就直接展示
- 🔧 核心优化：删除模糊判断（"生成中"等关键词），避免误判
- ✨ 透传原始响应：接口返回错误时完整展示 API 响应内容
- 🔧 参数调整：移除 --timeout CLI 参数

### v1.9.0
- 🔧 重构：按 SKILL.md 规范调整目录结构
- ✨ 新增：scripts/ 目录存放 generate.py
- ✨ 新增：LICENSE 文件（MIT）
- ✨ 新增：完整 SKILL.md（含 When to Use、Examples、Boundaries）
- 🔧 优化：完善 .gitignore，移除构建产物
- 🔧 优化：build.sh / release.sh 适配新结构

## License

MIT
