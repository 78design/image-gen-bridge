# image-gen-bridge

AI 图片生成工具，支持文生图和图生图。符合 SKILL.md 规范的标准技能包。

## 📦 当前版本

v1.9.1

## 🚀 安装方法

### 方法一：Git 克隆（所有 Agent 通用）

```bash
git clone https://github.com/78design/image-gen-bridge.git
cd image-gen-bridge
```

**方案 A：使用虚拟环境（推荐）**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

**方案 B：直接安装到当前 Python 环境**
```bash
pip install -r scripts/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

> ✅ 支持所有主流 AI Agent：Trae、Cursor、Claude Code、OpenCode 等
> 💡 macOS/Linux 用户若遇到 PEP 668 限制，可加 `--break-system-packages` 参数

### 方法二：使用 skilldirs 一键安装（仅 TRAE）

```bash
npx skilldirs add 78design/image-gen-bridge --yes --copy
cd ~/.trae-cn/skills/image-gen-bridge
pip install -r scripts/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 方法三：下载压缩包

[GitHub Releases v1.9.1](https://github.com/78design/image-gen-bridge/releases/tag/v1.9.1)

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

```bash
python scripts/generate.py --prompt "把这只猫放在沙发上" --image-file cat.png --output result.png
```

### 多张参考图

```bash
python scripts/generate.py --prompt "结合两张参考图" --image-file a.jpg --image-file b.jpg --output result.png
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
| `--image-file` | ❌ | 参考图片路径（可多次使用） |
| `--output` | ❌ | 输出文件路径 |
| `--aspect-ratio` | ❌ | 图片比例（默认 3:4） |
| `--api-url` | ❌ | 覆盖 API 地址 |
| `--api-key` | ❌ | 覆盖 API Key |
| `--model` | ❌ | 覆盖模型名称 |
| `--backup-model` | ❌ | 备用模型（默认 google/gemini-3.1-flash-image-preview） |

## 🔄 更新日志

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
