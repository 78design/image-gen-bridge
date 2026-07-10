#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image-gen-bridge - AI图片生成工具

设计原则：
- 不设请求超时（timeout=None），接口返回什么就拿到什么
- 正常情况提取图片 / base64 保存
- 异常情况把接口的原始响应直接透传给用户，不做模糊判断
"""

import argparse
import base64
import json
import os
import re
import sys

try:
    import requests
except ImportError:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    req_path = os.path.join(script_dir, "requirements.txt")
    print("Error: requests library not installed.")
    print(f"Please run: pip install -r {req_path} -i https://mirrors.aliyun.com/pypi/simple/")
    print("If you get PEP 668 error on macOS/Linux, add: --break-system-packages")
    sys.exit(1)

# 全局配置
DEFAULT_ASPECT_RATIO = "3:4"

# 比例到像素尺寸映射表
# OpenAI/DALL-E 等模型需要像素格式，如 "1024x1792"
ASPECT_RATIO_TO_SIZE = {
    "3:4": "1024x1792",    # 竖版（默认）
    "4:3": "1792x1024",    # 横版
    "1:1": "1024x1024",    # 方形
    "16:9": "1920x1080",   # 宽屏横版
    "9:16": "1080x1920",   # 宽屏竖版
    "21:9": "2048x878",    # 超宽屏
    "9:21": "878x2048",    # 超长竖版
}


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def download_image(url, output_path):
    """下载图片到本地。"""
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        response = requests.get(url, timeout=None)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def extract_images_from_response(result):
    """从 API 响应中提取所有图片 URL，支持多种格式。"""
    images = []

    if "choices" not in result or not result["choices"]:
        return images

    for idx, choice in enumerate(result["choices"]):
        message = choice.get("message", {})
        content = message.get("content", "")

        # 格式1: Markdown 图片 URL
        md_urls = re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', str(content))
        for url in md_urls:
            images.append({"index": idx, "url": url, "type": "markdown_url"})

        # 格式2: content 为数组
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "image_url":
                        img_url = item.get("image_url", {}).get("url", "")
                        if img_url:
                            images.append({"index": idx, "url": img_url, "type": "array_url"})
                    elif item.get("type") == "image_base64":
                        b64 = item.get("image_base64", "")
                        if b64:
                            images.append({"index": idx, "url": f"data:image/png;base64,{b64}", "type": "array_base64"})

        # 格式3: Gemini images 字段
        gemini_images = message.get("images", [])
        for img_data in gemini_images:
            img_url = img_data.get("image_url", {})
            if isinstance(img_url, dict):
                url = img_url.get("url", "")
            else:
                url = str(img_url)
            if url:
                images.append({"index": idx, "url": url, "type": "gemini_images"})

        # 格式4: OpenAI b64_json
        b64_json = message.get("b64_json", "")
        if b64_json:
            images.append({"index": idx, "url": f"data:image/png;base64,{b64_json}", "type": "b64_json"})

    return images


def save_extracted_images(extracted, output_path):
    """把提取到的图片列表落盘，返回保存后的路径列表。"""
    saved = []
    for img_info in extracted:
        image_url = img_info["url"]
        idx = img_info["index"]

        if not output_path:
            # 没有指定输出路径时，只打印 URL
            print(f"Image {idx+1} URL: {image_url}")
            saved.append(image_url)
            continue

        if image_url.startswith("data:image"):
            b64_data = image_url.split(",", 1)[1]
            image_data = base64.b64decode(b64_data)
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"Saved (base64): {output_path}")
            saved.append(output_path)
        else:
            print(f"Image {idx+1} URL: {image_url}")
            if download_image(image_url, output_path):
                print(f"Saved: {output_path}")
                saved.append(output_path)
    return saved


def dump_response(result, title):
    """把接口的完整响应原样输出，便于排查。"""
    print(f"\n{'='*60}")
    print(title)
    print(f"{'='*60}")
    try:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception:
        print(str(result))
    print(f"{'='*60}\n")


def generate_image(prompt, api_url, api_key, model, image_files=None, output_path=None,
                   aspect_ratio=DEFAULT_ASPECT_RATIO):
    """调用 API 生成图片，接口返回什么就拿到什么，不设超时，不做模糊判断。"""
    if not api_url.endswith("/chat/completions"):
        api_url = api_url.rstrip("/") + "/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # 比例同时通过 payload size 和 prompt 文本下发，提高兼容性
    if aspect_ratio:
        prompt_with_ratio = f"{prompt}，图片比例为{aspect_ratio}"
    else:
        prompt_with_ratio = prompt

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt_with_ratio}]}]

    if image_files and len(image_files) > 0:
        valid_images = [f for f in image_files if os.path.exists(f)]
        if valid_images:
            print(f"Mode: Image-to-Image (refs: {', '.join(valid_images)})")
            for image_file in valid_images:
                img_base64 = encode_image_to_base64(image_file)
                ext = os.path.splitext(image_file)[1].lower()
                mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{img_base64}"}
                })
        else:
            print("Warning: No valid reference images, using text-to-image mode")
    else:
        print("Mode: Text-to-Image")

    print(f"Model: {model}\nAPI: {api_url}\nAspect ratio: {aspect_ratio}\nPrompt: {prompt_with_ratio[:80]}...")

    payload = {
        "model": model,
        "messages": messages
    }

    if aspect_ratio:
        pixel_size = ASPECT_RATIO_TO_SIZE.get(aspect_ratio, ASPECT_RATIO_TO_SIZE[DEFAULT_ASPECT_RATIO])
        payload["size"] = pixel_size

    # 单次请求，不设超时（timeout=None）
    # 接口返回什么就直接处理什么：拿到图片就保存，拿不到就把接口的响应原样展示
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=None)
    except requests.exceptions.RequestException as e:
        # 仅在网络层错误（连接失败、DNS 解析失败等）时返回 None
        print(f"\n{'='*60}")
        print(f"Network Error")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"{'='*60}\n")
        return None

    # 非 200：直接把接口的响应体原样透传
    if response.status_code != 200:
        print(f"\n[API Response Status]: {response.status_code}")
        try:
            err_body = response.json()
            dump_response(err_body, f"API Error Response (HTTP {response.status_code})")
        except Exception:
            print(f"\n{'='*60}")
            print(f"API Error Response (HTTP {response.status_code})")
            print(f"{'='*60}")
            print(response.text)
            print(f"{'='*60}\n")
        return None

    # 200 但响应不是 JSON：原样输出
    try:
        result = response.json()
    except Exception as e:
        print(f"\n[API Response Status]: 200 (not JSON)")
        print(f"\n{'='*60}")
        print(f"Response Parse Error")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"Raw: {response.text[:2000]}")
        print(f"{'='*60}\n")
        return None

    # 提取图片
    extracted = extract_images_from_response(result)
    if extracted:
        saved = save_extracted_images(extracted, output_path)
        if saved:
            print(f"\nSuccessfully generated {len(saved)} image(s)")
            print(f"Model used: {model}")
            return saved[0] if output_path else (saved if len(saved) > 1 else saved[0])

    # 拿到响应但没图片：把接口的完整响应原样展示给用户
    print(f"\n[API Response Status]: 200")
    dump_response(result, "No Images in Response")
    return None


def main():
    parser = argparse.ArgumentParser(description="image-gen-bridge - AI Image Generation",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
Examples:
  python generate.py --prompt "A cute cat" --output cat.png
  python generate.py --prompt "Style transfer" --image-file ref.jpg --output result.jpg
  python generate.py --prompt "Combine styles" --image-file a.jpg --image-file b.jpg --output combined.png
  python generate.py --prompt "A sunset" --output sunset.png
  (Automatically falls back to google/gemini-3.1-flash-image-preview)

Note:
  Use --backup-model to automatically switch if primary model fails.
  No request timeout - waits for the API to return whatever it returns.

Environment Variables:
  IMAGE_GEN_API_KEY    Required
  IMAGE_GEN_API_URL    Default: https://api.1openapi.com/v1
  IMAGE_GEN_MODEL      Default: openai/gpt-image-2
                                     """)

    parser.add_argument("--prompt", required=True, help="Text prompt")
    parser.add_argument("--image-file", action="append", help="Reference image(s)")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--aspect-ratio", "--ratio", default="3:4", help="Image aspect ratio (default: 3:4, e.g., 1:1, 16:9, 9:16)")
    parser.add_argument("--backup-model", default="google/gemini-3.1-flash-image-preview", help="Backup model if primary fails (default: google/gemini-3.1-flash-image-preview)")
    parser.add_argument("--api-url", help="API URL")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--model", help="Model name")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("IMAGE_GEN_API_KEY")
    api_url = args.api_url or os.environ.get("IMAGE_GEN_API_URL", "https://api.1openapi.com/v1")
    model = args.model or os.environ.get("IMAGE_GEN_MODEL", "openai/gpt-image-2")

    if not api_key:
        print("Error: API key required. Set via --api-key or IMAGE_GEN_API_KEY")
        sys.exit(1)

    if len(api_key) < 10:
        print("Error: Invalid API key format.")
        print("API key should be at least 10 characters long.")
        sys.exit(1)

    print("Generating image...")
    print("  → Connecting to API...")

    # 尝试主模型
    result = generate_image(args.prompt, api_url, api_key, model, args.image_file, args.output,
                            args.aspect_ratio)

    # 如果主模型失败且有备用模型，自动切换
    if not result and args.backup_model:
        print(f"\n{'='*60}")
        print(f"Primary model failed, switching to backup model: {args.backup_model}")
        print(f"{'='*60}\n")
        result = generate_image(args.prompt, api_url, api_key, args.backup_model, args.image_file, args.output,
                                args.aspect_ratio)

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
