#!/usr/bin/env python3
"""Image generation script using 1openapi API with image reference support."""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Run: pip install requests")
    sys.exit(1)

API_KEY = os.environ.get("IMAGE_GEN_API_KEY")
if not API_KEY:
    print("Error: IMAGE_GEN_API_KEY environment variable not set")
    print("Please set your API key: export IMAGE_GEN_API_KEY='your-api-key'")
    sys.exit(1)
API_URL = "https://api.1openapi.com/v1/chat/completions"
MODEL = "openai/gpt-image-2"


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
        print(f"   下载图片失败: {e}")
        return False


def extract_image_url_from_markdown(content):
    """Extract image URL from markdown content."""
    pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None


def generate_image(prompt, image_file=None, output_path=None):
    """Generate image using the API."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "user", "content": []}]
    
    messages[0]["content"].append({
        "type": "text",
        "text": prompt
    })
    
    if image_file and os.path.exists(image_file):
        print(f"   模式: 图生图(文件: {image_file})")
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
        print("   模式: 文生图")
    
    print(f"   提示词: {prompt}")
    
    payload = {
        "model": MODEL,
        "messages": messages
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            content = message.get("content", "")
            
            image_url = extract_image_url_from_markdown(content)
            if image_url:
                print(f"   获取到图片URL: {image_url}")
                if output_path:
                    if download_image(image_url, output_path):
                        print(f"\n✅ 图片已保存: {output_path}")
                        return output_path
                return image_url
            
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "image_url":
                        image_url = item.get("image_url", {}).get("url", "")
                        if image_url.startswith("data:image"):
                            base64_data = image_url.split(",")[1]
                            image_data = base64.b64decode(base64_data)
                            if output_path:
                                with open(output_path, "wb") as f:
                                    f.write(image_data)
                                print(f"\n✅ 图片已保存: {output_path}")
                                return output_path
        
        print(f"\n❌ 生成失败: 无法从响应中提取图片")
        return None
        
    except requests.exceptions.Timeout:
        print("\n❌ 生成失败: API请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 生成失败: API请求失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate images using 1openapi API")
    parser.add_argument("--prompt", required=True, help="Text prompt for image generation")
    parser.add_argument("--image-file", help="Path to reference image file (for image-to-image)")
    parser.add_argument("--output", help="Output path for generated image")
    
    args = parser.parse_args()
    
    print("正在生成图片...")
    result = generate_image(args.prompt, args.image_file, args.output)
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
