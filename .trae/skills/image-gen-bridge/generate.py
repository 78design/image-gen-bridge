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


def extract_image_url_from_markdown(content):
    """Extract image URL from markdown content."""
    pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None


def generate_image(prompt, api_url, api_key, model, image_files=None, output_path=None, n=1):
    """Generate image using OpenAI-compatible API."""

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
    print(f"   Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")

    payload = {
        "model": model,
        "messages": messages,
        "n": n
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()

        results = []
        
        if "choices" in result and len(result["choices"]) > 0:
            for idx, choice in enumerate(result["choices"]):
                message = choice.get("message", {})
                content = message.get("content", "")
                image_url = None
                
                # Try extract image URL from markdown response
                extracted_url = extract_image_url_from_markdown(str(content))
                if extracted_url:
                    image_url = extracted_url
                # Try extract base64 image from array response
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "image_url":
                            img_url = item.get("image_url", {}).get("url", "")
                            if img_url.startswith("data:image"):
                                image_url = img_url

                if image_url:
                    print(f"   Image {idx+1} URL: {image_url}")
                    
                    if output_path:
                        # Generate output filename with index
                        if n > 1:
                            path_obj = Path(output_path)
                            numbered_output = str(path_obj.parent / f"{path_obj.stem}_{idx+1}{path_obj.suffix}")
                        else:
                            numbered_output = output_path
                        
                        # Create output directory if needed
                        output_dir = os.path.dirname(numbered_output)
                        if output_dir and not os.path.exists(output_dir):
                            os.makedirs(output_dir, exist_ok=True)
                        
                        # Download or save base64
                        if image_url.startswith("data:image"):
                            base64_data = image_url.split(",")[1]
                            image_data = base64.b64decode(base64_data)
                            with open(numbered_output, "wb") as f:
                                f.write(image_data)
                            print(f"   Saved: {numbered_output}")
                            results.append(numbered_output)
                        else:
                            if download_image(image_url, numbered_output):
                                print(f"   Saved: {numbered_output}")
                                results.append(numbered_output)
                    else:
                        results.append(image_url)

        if results:
            print(f"\n   Successfully generated {len(results)} image(s)")
            return results if len(results) > 1 else results[0]
        
        print(f"\n   Failed: Cannot extract images from response")
        return None

    except requests.exceptions.Timeout:
        print("\n   Failed: API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n   Failed: API request error - {e}")
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

  # Custom API endpoint and model
  python generate.py --prompt "A sunset landscape" \\
    --api-url "https://your-proxy.com/v1" \\
    --model "dall-e-3" \\
    --output sunset.png

Environment Variables:
  IMAGE_GEN_API_KEY    API key (required)
  IMAGE_GEN_API_URL    API base URL (default: https://api.openai.com/v1)
  IMAGE_GEN_MODEL      Default model name
        """
    )

    parser.add_argument("--prompt", required=True, help="Text prompt for image generation")
    parser.add_argument("--image-file", action="append", help="Path to reference image (image-to-image mode, multiple allowed)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--number", "-n", type=int, default=1, help="Number of images to generate (default: 1)")
    parser.add_argument("--api-url", help="API base URL (or set IMAGE_GEN_API_URL)")
    parser.add_argument("--api-key", help="API key (or set IMAGE_GEN_API_KEY)")
    parser.add_argument("--model", help="Model name (or set IMAGE_GEN_MODEL)")

    args = parser.parse_args()

    # Get config from args or environment variables
    api_key = args.api_key or os.environ.get("IMAGE_GEN_API_KEY")
    api_url = args.api_url or os.environ.get("IMAGE_GEN_API_URL", "https://api.openai.com/v1")
    model = args.model or os.environ.get("IMAGE_GEN_MODEL", "gpt-image-1")

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
        n=args.number
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
