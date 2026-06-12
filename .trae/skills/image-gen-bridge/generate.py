#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
image-gen-bridge - AI图片生成工具

通过OpenAI兼容接口调用各类生图模型，支持文生图和图生图。
适用于各种OpenAI兼容的中转站/代理服务。
"""

import argparse
import base64
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not installed.")
    print("Run: pip install requests")
    sys.exit(1)

# 全局配置
MAX_RETRIES = 2
DEFAULT_TIMEOUT = 180


def encode_image_to_base64(image_path):
    """Encode image file to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def download_image(url, output_path):
    """Download image from URL and save to file."""
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"   Download failed: {e}")
        return False


def extract_images_from_response(result):
    """从 API 响应中提取所有图片 URL，支持多种格式。

    支持格式：
    - Markdown: ![alt](https://...)
    - Base64: data:image/png;base64,...
    - Gemini images 字段: choice["message"]["images"][...]["image_url"]["url"]
    - OpenAI b64_json: choice["message"]["b64_json"]
    """
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

        # 格式2: content 为数组（OpenAI 图片数组格式）
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

        # 格式4: OpenAI b64_json 字段
        b64_json = message.get("b64_json", "")
        if b64_json:
            images.append({"index": idx, "url": f"data:image/png;base64,{b64_json}", "type": "b64_json"})

    return images


def is_generating_response(result):
    """检测是否为'生成中'等无效响应。"""
    if "choices" not in result or not result["choices"]:
        return False, ""

    for choice in result["choices"]:
        content = str(choice.get("message", {}).get("content", ""))
        # 检测常见生成中提示词
        generating_patterns = [
            "生成中", "generating", "正在生成", "稍候", "负载较高",
            "请稍候", "Processing", "生图失败", "失败", "error", "Error",
            "❌", "Failed", "failed"
        ]
        # 如果内容很短且包含这些关键词，认为是无效响应
        if any(p in content for p in generating_patterns) and len(content) < 500:
            return True, content[:300]

    return False, ""


def extract_error_detail(result):
    """从 API 响应中提取错误详情。"""
    # 顶层 error 字段
    if "error" in result:
        err = result["error"]
        if isinstance(err, dict):
            return err.get("message") or err.get("detail") or str(err)
        return str(err)

    # 顶层 detail 字段
    if "detail" in result:
        return result["detail"]

    # choices 里的 error
    if "choices" in result:
        for choice in result.get("choices", []):
            msg = str(choice.get("message", {}).get("content", ""))
            if any(p in msg for p in ["❌", "失败", "error", "Error", "failed"]):
                return msg.strip()

    return None


def generate_image(prompt, api_url, api_key, model, image_files=None, output_path=None,
                   n=1, aspect_ratio="3:4", timeout=DEFAULT_TIMEOUT):
    """Generate image using OpenAI-compatible API with retry support."""

    # Ensure api_url ends with /chat/completions
    if not api_url.endswith("/chat/completions"):
        if api_url.endswith("/"):
            api_url = api_url + "chat/completions"
        else:
            api_url = api_url + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    if aspect_ratio:
        prompt = f"{prompt}，图片比例为{aspect_ratio}"

    messages = [{"role": "user", "content": []}]

    # Add text prompt
    messages[0]["content"].append({
        "type": "text",
        "text": prompt
    })

    # Add reference images if provided
    if image_files and len(image_files) > 0:
        valid_images = []
        for image_file in image_files:
            if os.path.exists(image_file):
                valid_images.append(image_file)
            else:
                print(f"   Warning: Image file not found: {image_file}")

        if valid_images:
            print(f"   Mode: Image-to-Image (refs: {', '.join(valid_images)})")
            for image_file in valid_images:
                image_base64 = encode_image_to_base64(image_file)
                image_ext = Path(image_file).suffix.lower()
                mime_type = "image/jpeg" if image_ext in [".jpg", ".jpeg"] else "image/png"

                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}"
                    }
                })
        else:
            print("   Warning: No valid reference images found")
            print("   Falling back to text-to-image mode.")
    else:
        print("   Mode: Text-to-Image")

    print(f"   Model: {model}")
    print(f"   API: {api_url}")
    print(f"   Number of images: {n}")
    print(f"   Aspect ratio: {aspect_ratio}")
    print(f"   Timeout: {timeout}s")
    print(f"   Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")

    payload = {
        "model": model,
        "messages": messages,
        "n": n
    }

    results = []
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n   [Attempt {attempt}/{MAX_RETRIES}]")

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)

            # HTTP 错误状态码
            if response.status_code != 200:
                try:
                    err_body = response.json()
                except Exception:
                    err_body = {"raw": response.text[:500]}
                err_detail = extract_error_detail(err_body)
                print(f"   HTTP {response.status_code} Error: {err_detail or response.text[:200]}")
                last_error = f"HTTP {response.status_code}: {err_detail or response.text[:200]}"
                if attempt < MAX_RETRIES:
                    print(f"   Retrying...")
                    continue
                break

            result = response.json()

            # 检测 "生成中" 无效响应
            is_gen, gen_content = is_generating_response(result)
            if is_gen:
                print(f"   Warning: API returned generating status: {gen_content[:200]}")
                last_error = f"Backend not ready: {gen_content[:200]}"
                if attempt < MAX_RETRIES:
                    print(f"   Retrying...")
                    continue
                continue

            # 提取错误
            err_detail = extract_error_detail(result)
            if err_detail and not is_generating_response(result)[0]:
                print(f"   API Error: {err_detail}")
                last_error = err_detail
                if attempt < MAX_RETRIES:
                    print(f"   Retrying...")
                    continue
                continue

            # 提取图片
            extracted = extract_images_from_response(result)

            if not extracted:
                # 打印原始响应方便调试
                raw_content = str(result.get("choices", [{}])[0].get("message", {}).get("content", ""))[:300]
                print(f"   No images extracted. Raw content: {raw_content}")
                last_error = f"No images in response: {raw_content}"
                if attempt < MAX_RETRIES:
                    print(f"   Retrying...")
                    continue
                continue

            # 保存图片
            for img_info in extracted:
                image_url = img_info["url"]
                idx = img_info["index"]

                if output_path:
                    if n > 1:
                        path_obj = Path(output_path)
                        numbered_output = str(path_obj.parent / f"{path_obj.stem}_{idx+1}{path_obj.suffix}")
                    else:
                        numbered_output = output_path

                    output_dir = os.path.dirname(numbered_output)
                    if output_dir and not os.path.exists(output_dir):
                        os.makedirs(output_dir, exist_ok=True)

                    if image_url.startswith("data:image"):
                        b64_data = image_url.split(",", 1)[1]
                        image_data = base64.b64decode(b64_data)
                        with open(numbered_output, "wb") as f:
                            f.write(image_data)
                        print(f"   Saved (base64): {numbered_output}")
                        results.append(numbered_output)
                    else:
                        print(f"   Image {idx+1} URL: {image_url}")
                        if download_image(image_url, numbered_output):
                            print(f"   Saved: {numbered_output}")
                            results.append(numbered_output)
                else:
                    print(f"   Image {idx+1} URL: {image_url}")
                    results.append(image_url)

            if results:
                print(f"\n   Successfully generated {len(results)} image(s)")
                return results if len(results) > 1 else results[0]

        except requests.exceptions.Timeout:
            print(f"   Request timed out after {timeout}s")
            last_error = f"Timeout after {timeout}s"
            if attempt < MAX_RETRIES:
                print(f"   Retrying...")
                continue
        except requests.exceptions.RequestException as e:
            print(f"   Request error: {e}")
            last_error = str(e)
            if attempt < MAX_RETRIES:
                print(f"   Retrying...")
                continue

    print(f"\n   Failed after {MAX_RETRIES} attempts. Last error: {last_error}")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="image-gen-bridge - AI Image Generation via OpenAI-compatible API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text-to-Image (single)
  python generate.py --prompt "A cute cat" --output cat.png

  # Text-to-Image (multiple, 4 images)
  python generate.py --prompt "A cute cat" --number 4 --output cat.png

  # Image-to-Image (with single reference)
  python generate.py --prompt "A woman wearing this keychain" \\
    --image-file product.jpg --output fashion.png

  # Image-to-Image (with multiple references)
  python generate.py --prompt "Combine the style of both images" \\
    --image-file style1.jpg --image-file style2.jpg --output combined.png

  # Custom timeout (in seconds)
  python generate.py --prompt "A sunset landscape" \\
    --timeout 300 --output sunset.png

Note:
  When using --number > 1, some API providers may not support
  multi-image generation and only return 1 image. If this happens,
  use --number 1 with different prompts or seeds.

Environment Variables:
  IMAGE_GEN_API_KEY    API key (required)
  IMAGE_GEN_API_URL    API base URL (default: https://api.1openapi.com/v1)
  IMAGE_GEN_MODEL      Default model name
        """
    )

    parser.add_argument("--prompt", required=True, help="Text prompt for image generation")
    parser.add_argument("--image-file", action="append", help="Path to reference image (image-to-image mode, multiple allowed)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--number", "-n", type=int, default=1, help="Number of images to generate (default: 1)")
    parser.add_argument("--aspect-ratio", "--ratio", default="3:4", help="Image aspect ratio (default: 3:4, e.g., 1:1, 16:9, 9:16)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--api-url", help="API base URL (or set IMAGE_GEN_API_URL)")
    parser.add_argument("--api-key", help="API key (or set IMAGE_GEN_API_KEY)")
    parser.add_argument("--model", help="Model name (or set IMAGE_GEN_MODEL)")

    args = parser.parse_args()

    # Get config from args or environment variables
    api_key = args.api_key or os.environ.get("IMAGE_GEN_API_KEY")
    api_url = args.api_url or os.environ.get("IMAGE_GEN_API_URL", "https://api.1openapi.com/v1")
    model = args.model or os.environ.get("IMAGE_GEN_MODEL", "openai/gpt-image-2")

    if not api_key:
        print("Error: API key is required.")
        print("Set via --api-key or environment variable IMAGE_GEN_API_KEY")
        sys.exit(1)

    if len(api_key) < 10:
        print("Error: Invalid API key format.")
        print("API key should be at least 10 characters long.")
        sys.exit(1)

    print("Generating image...")
    print("  → Connecting to API...")
    result = generate_image(
        prompt=args.prompt,
        api_url=api_url,
        api_key=api_key,
        model=model,
        image_files=args.image_file,
        output_path=args.output,
        n=args.number,
        aspect_ratio=args.aspect_ratio,
        timeout=args.timeout
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
