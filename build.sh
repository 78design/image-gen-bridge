#!/bin/bash
# image-gen-bridge - Build Release Package
# Usage: ./build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION=$(cat "$SCRIPT_DIR/VERSION")
PACKAGE_NAME="image-gen-bridge-v${VERSION}"
BUILD_DIR="$SCRIPT_DIR/build"
PACKAGE_FILE="$SCRIPT_DIR/${PACKAGE_NAME}.zip"

echo ""
echo "========================================="
echo "  image-gen-bridge - Build Script"
echo "========================================="
echo ""
echo "Version: $VERSION"
echo "Package: $PACKAGE_FILE"
echo ""

rm -rf "$BUILD_DIR" "$PACKAGE_FILE"
mkdir -p "$BUILD_DIR/$PACKAGE_NAME"

# 复制核心文件
cp "$SCRIPT_DIR/README.md" "$BUILD_DIR/$PACKAGE_NAME/"
cp "$SCRIPT_DIR/SKILL.md" "$BUILD_DIR/$PACKAGE_NAME/"
cp "$SCRIPT_DIR/generate.py" "$BUILD_DIR/$PACKAGE_NAME/"
cp "$SCRIPT_DIR/requirements.txt" "$BUILD_DIR/$PACKAGE_NAME/"
cp "$SCRIPT_DIR/VERSION" "$BUILD_DIR/$PACKAGE_NAME/"

# 创建压缩包
cd "$BUILD_DIR"
zip -r "$PACKAGE_FILE" "$PACKAGE_NAME/" > /dev/null
cd "$SCRIPT_DIR"

# 清理
rm -rf "$BUILD_DIR"

echo "Built: $PACKAGE_FILE"
ls -lh "$PACKAGE_FILE"
echo ""
echo "========================================="
echo "  Build completed!"
echo "========================================="
echo ""
echo "Upload to: https://github.com/78design/image-gen-bridge/releases/tag/v$VERSION"
echo ""
