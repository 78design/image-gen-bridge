# Image Generator Skill

AI图片生成技能，支持文生图和图生图（参考图模式）。

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/tianhui/image-generator-skill.git
cd image-generator-skill
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API Key

**必须设置环境变量**，技能不包含任何内置API key：

```bash
export IMAGE_GEN_API_KEY="your-api-key-here"
```

建议添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export IMAGE_GEN_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

## 使用方法

### 文生图

```bash
python generate.py --prompt "A cute cat sitting on a sofa" --output cat.png
```

### 图生图（参考图模式）

```bash
python generate.py --prompt "A stylish woman carrying this bag charm" \
  --image-file reference.jpg \
  --output output.png
```

## 参数说明

| 参数 | 说明 | 必需 |
|------|------|------|
| `--prompt` | 图片描述文本 | ✅ |
| `--image-file` | 参考图片路径（图生图模式） | ❌ |
| `--output` | 输出图片路径 | ❌ |

## 使用场景示例

### 电商产品穿搭图

```bash
python generate.py \
  --prompt "A stylish 22-year-old Chinese woman with long wavy hair, wearing a white cropped t-shirt and high-waisted jeans, carrying a black crossbody bag with a pink plush keychain hanging from it. Walking on a trendy city street, fashion editorial photography style" \
  --image-file product.jpg \
  --output fashion_shot.png
```

## 注意事项

- API key必须自行申请（1openapi平台）
- 图片生成可能需要10-30秒，请耐心等待
- 参考图模式会保持产品特征一致性

## 依赖

- Python 3.7+
- requests >= 2.31.0
