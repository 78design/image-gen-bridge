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


def extract_image_url(content):
    pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    match = re.search(pattern, str(content))
    return match.group(1) if match else None


def generate_image(prompt, api_url, api_key, model, image_files=None, output_path=None, n=1, aspect_ratio="3:4"):
    if not api_url.endswith("/chat/completions"):
        api_url = api_url.rstrip("/") + "/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    if aspect_ratio:
        prompt = f"{prompt}，图片比例为{aspect_ratio}"

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

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

    print(f"Model: {model}\nAPI: {api_url}\nNumber of images: {n}\nAspect ratio: {aspect_ratio}\nPrompt: {prompt[:80]}...")

    try:
        payload = {
            "model": model,
            "messages": messages,
            "n": n
        }
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"API Error: {result['error'].get('message', 'Unknown error')}")
            return None

        results = []
        
        if "choices" in result and len(result["choices"]) > 0:
            for idx, choice in enumerate(result["choices"]):
                content = choice["message"].get("content", "")
                image_url = extract_image_url(content)

                if image_url:
                    print(f"Image {idx+1} URL: {image_url}")
                    
                    if output_path:
                        if n > 1:
                            path_dir, path_base = os.path.split(output_path)
                            path_name, path_ext = os.path.splitext(path_base)
                            numbered_output = os.path.join(path_dir, f"{path_name}_{idx+1}{path_ext}")
                        else:
                            numbered_output = output_path
                        
                        if download_image(image_url, numbered_output):
                            print(f"Saved: {numbered_output}")
                            results.append(numbered_output)
                    else:
                        results.append(image_url)

        if results:
            print(f"Successfully generated {len(results)} image(s)")
            return results if len(results) > 1 else results[0]

        print("Failed: Cannot extract image from response")
        return None

    except requests.exceptions.Timeout:
        print("Failed: Request timed out")
        return None
    except Exception as e:
        print(f"Failed: {e}")
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

Environment Variables:
  IMAGE_GEN_API_KEY    Required
  IMAGE_GEN_API_URL    Default: https://api.openai.com/v1
  IMAGE_GEN_MODEL      Default: openai/gpt-image-2
                                     """)

    parser.add_argument("--prompt", required=True, help="Text prompt")
    parser.add_argument("--image-file", action="append", help="Reference image(s)")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--number", "-n", type=int, default=1, help="Number of images to generate (default: 1)")
    parser.add_argument("--aspect-ratio", "--ratio", default="3:4", help="Image aspect ratio (default: 3:4, e.g., 1:1, 16:9, 9:16)")
    parser.add_argument("--api-url", help="API URL")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--model", help="Model name")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("IMAGE_GEN_API_KEY")
    api_url = args.api_url or os.environ.get("IMAGE_GEN_API_URL", "https://api.openai.com/v1")
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
    result = generate_image(args.prompt, api_url, api_key, model, args.image_file, args.output, args.number, args.aspect_ratio)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()