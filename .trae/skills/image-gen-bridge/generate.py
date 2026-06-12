#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image-gen-bridge - AI图片生成工具"""

import argparse
import base64
import os
import re
import sys

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Run: pip install requests")
    sys.exit(1)

# 全局配置
MAX_RETRIES = 2
DEFAULT_TIMEOUT = 180
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
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        response = requests.get(url, timeout=60)
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


def is_generating_response(result):
    """检测是否为'生成中'等无效响应。"""
    if "choices" not in result or not result["choices"]:
        return False, ""

    for choice in result["choices"]:
        content = str(choice.get("message", {}).get("content", ""))
        patterns = [
            "生成中", "generating", "正在生成", "稍候", "负载较高",
            "请稍候", "Processing", "生图失败", "失败", "error", "Error",
            "❌", "Failed", "failed"
        ]
        if any(p in content for p in patterns) and len(content) < 500:
            return True, content[:300]

    return False, ""


def extract_error_detail(result):
    """从 API 响应中提取错误详情。"""
    if "error" in result:
        err = result["error"]
        if isinstance(err, dict):
            return err.get("message") or err.get("detail") or str(err)
        return str(err)

    if "detail" in result:
        return result["detail"]

    if "choices" in result:
        for choice in result.get("choices", []):
            msg = str(choice.get("message", {}).get("content", ""))
            if any(p in msg for p in ["❌", "失败", "error", "Error", "failed"]):
                return msg.strip()

    return None


def generate_image(prompt, api_url, api_key, model, image_files=None, output_path=None,
                   n=1, aspect_ratio=DEFAULT_ASPECT_RATIO, timeout=DEFAULT_TIMEOUT):
    if not api_url.endswith("/chat/completions"):
        api_url = api_url.rstrip("/") + "/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # 同时支持两种方式：payload size 参数 + prompt 文本补充
    # 有些 API 支持 size 参数，有些不支持，两种都传提高兼容性
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

    print(f"Model: {model}\nAPI: {api_url}\nNumber of images: {n}\nAspect ratio: {aspect_ratio}\nTimeout: {timeout}s\nPrompt: {prompt_with_ratio[:80]}...")

    payload = {
        "model": model,
        "messages": messages,
        "n": n
    }

    # 添加 size 参数（部分 API 支持）
    # 将比例格式转换为像素格式，如 "3:4" -> "1024x1792"
    if aspect_ratio:
        pixel_size = ASPECT_RATIO_TO_SIZE.get(aspect_ratio, ASPECT_RATIO_TO_SIZE[DEFAULT_ASPECT_RATIO])
        payload["size"] = pixel_size

    results = []
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n[Attempt {attempt}/{MAX_RETRIES}]")

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)

            if response.status_code != 200:
                print(f"\n{'='*60}")
                print(f"API HTTP Error: {response.status_code}")
                print(f"{'='*60}")
                # 尝试解析 JSON 错误并完整输出
                try:
                    err_body = response.json()
                    import json
                    print(f"\n[API Response Body]:")
                    print(json.dumps(err_body, indent=2, ensure_ascii=False))
                except Exception:
                    print(f"\n[Raw Response]: {response.text}")
                print(f"{'='*60}\n")
                last_error = f"HTTP {response.status_code}: {response.text[:500]}"
                if attempt < MAX_RETRIES:
                    print("Retrying...")
                    continue
                break

            result = response.json()

            # 【关键】先提取图片，提取到了就直接保存，不检查"生成中"
            # 避免误判：有些API返回"生成中"文字+图片URL，图片有效不应丢弃
            extracted = extract_images_from_response(result)

            if extracted:
                # 有图片，直接保存
                for img_info in extracted:
                    image_url = img_info["url"]
                    idx = img_info["index"]

                    if output_path:
                        if n > 1:
                            path_dir, path_base = os.path.split(output_path)
                            path_name, path_ext = os.path.splitext(path_base)
                            numbered_output = os.path.join(path_dir, f"{path_name}_{idx+1}{path_ext}")
                        else:
                            numbered_output = output_path

                        if image_url.startswith("data:image"):
                            b64_data = image_url.split(",", 1)[1]
                            image_data = base64.b64decode(b64_data)
                            with open(numbered_output, "wb") as f:
                                f.write(image_data)
                            print(f"Saved (base64): {numbered_output}")
                            results.append(numbered_output)
                        else:
                            print(f"Image {idx+1} URL: {image_url}")
                            if download_image(image_url, numbered_output):
                                print(f"Saved: {numbered_output}")
                                results.append(numbered_output)
                    else:
                        print(f"Image {idx+1} URL: {image_url}")
                        results.append(image_url)

                if results:
                    print(f"\nSuccessfully generated {len(results)} image(s)")
                    return results if len(results) > 1 else results[0]

            # 没提取到图片，检查是否是"生成中"或错误
            is_gen, gen_content = is_generating_response(result)
            if is_gen:
                print(f"\n{'='*60}")
                print(f"Backend Not Ready (生成中)")
                print(f"{'='*60}")
                print(f"[Raw Response Content]:\n{gen_content}")
                print(f"{'='*60}\n")
                last_error = f"Backend not ready: {gen_content}"
                if attempt < MAX_RETRIES:
                    print("Retrying...")
                    continue
                continue

            # 检查错误信息 - 完整输出
            err_detail = extract_error_detail(result)
            if err_detail:
                print(f"\n{'='*60}")
                print(f"API Error Detected")
                print(f"{'='*60}")
                import json
                print(f"[Full API Response]:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print(f"{'='*60}\n")
                last_error = err_detail
                if attempt < MAX_RETRIES:
                    print("Retrying...")
                    continue
                continue

            # 既没图片也没明确错误，输出原始内容
            raw_content = str(result.get("choices", [{}])[0].get("message", {}).get("content", ""))[:500]
            print(f"\n{'='*60}")
            print(f"No Images Extracted")
            print(f"{'='*60}")
            print(f"[Raw Response Content]:\n{raw_content}")
            print(f"[Full API Response]:")
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
            print(f"{'='*60}\n")
            last_error = f"No images in response: {raw_content}"
            if attempt < MAX_RETRIES:
                print("Retrying...")
                continue
            continue

        except requests.exceptions.Timeout:
            print(f"\n{'='*60}")
            print(f"Request Timeout")
            print(f"{'='*60}")
            print(f"Timeout after {timeout}s")
            print(f"This usually means:")
            print(f"  - API server is overloaded")
            print(f"  - Network connectivity issues")
            print(f"  - Image generation takes too long")
            print(f"  - Try increasing --timeout parameter")
            print(f"{'='*60}\n")
            last_error = f"Timeout after {timeout}s"
            if attempt < MAX_RETRIES:
                print("Retrying...")
                continue
        except requests.exceptions.ConnectionError as e:
            print(f"\n{'='*60}")
            print(f"Connection Error")
            print(f"{'='*60}")
            print(f"Error: {e}")
            print(f"This usually means:")
            print(f"  - API server is down")
            print(f"  - Network connectivity issues")
            print(f"  - Firewall blocking the request")
            print(f"{'='*60}\n")
            last_error = f"Connection error: {e}"
            if attempt < MAX_RETRIES:
                print("Retrying...")
                continue
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"Request Error")
            print(f"{'='*60}")
            print(f"Error: {e}")
            print(f"{'='*60}\n")
            last_error = str(e)
            if attempt < MAX_RETRIES:
                print("Retrying...")
                continue

    print(f"\n{'='*60}")
    print(f"Failed after {MAX_RETRIES} attempts")
    print(f"{'='*60}")
    print(f"Last Error: {last_error}")
    print(f"\nNote: If this is a third-party API, instability is normal.")
    print(f"Wait for the API to recover and try again.")
    print(f"{'='*60}")
    return None


def main():
    parser = argparse.ArgumentParser(description="image-gen-bridge - AI Image Generation",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
Examples:
  python generate.py --prompt "A cute cat" --output cat.png
  python generate.py --prompt "A cute cat" --number 4 --output cat.png
  python generate.py --prompt "Style transfer" --image-file ref.jpg --output result.png
  python generate.py --prompt "Combine styles" --image-file a.jpg --image-file b.jpg --output combined.png
  python generate.py --prompt "A sunset" --timeout 300 --output sunset.png

Note:
  When using --number > 1, some API providers may not support
  multi-image generation and only return 1 image.

Environment Variables:
  IMAGE_GEN_API_KEY    Required
  IMAGE_GEN_API_URL    Default: https://api.1openapi.com/v1
  IMAGE_GEN_MODEL      Default: openai/gpt-image-2
                                     """)

    parser.add_argument("--prompt", required=True, help="Text prompt")
    parser.add_argument("--image-file", action="append", help="Reference image(s)")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--number", "-n", type=int, default=1, help="Number of images to generate (default: 1)")
    parser.add_argument("--aspect-ratio", "--ratio", default="3:4", help="Image aspect ratio (default: 3:4, e.g., 1:1, 16:9, 9:16)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})")
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
    result = generate_image(args.prompt, api_url, api_key, model, args.image_file, args.output,
                            args.number, args.aspect_ratio, args.timeout)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
