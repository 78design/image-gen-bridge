#!/bin/bash
# image-gen-bridge - Automated Release Script
# Usage: ./release.sh <new_version>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <new_version>"
    echo "Example: $0 1.8.2"
    exit 1
fi

NEW_VERSION="$1"
CURRENT_VERSION=$(cat VERSION)

echo ""
echo "========================================="
echo "  image-gen-bridge - Release Script"
echo "========================================="
echo ""
echo "Current version: $CURRENT_VERSION"
echo "New version:     $NEW_VERSION"
echo ""

read -p "Continue with release? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Release cancelled."
    exit 0
fi

echo ""
echo "[1/5] Updating VERSION files..."
echo "$NEW_VERSION" > VERSION
echo "$NEW_VERSION" > .trae/skills/image-gen-bridge/VERSION
echo "   Done."

echo ""
echo "[2/5] Updating README.md files..."
for README in README.md .trae/skills/image-gen-bridge/README.md; do
    sed -i "s/v$CURRENT_VERSION/v$NEW_VERSION/g" "$README"
    sed -i "s/image-gen-bridge-v$CURRENT_VERSION/image-gen-bridge-v$NEW_VERSION/g" "$README"
done
echo "   Done."

echo ""
echo "[3/5] Updating CHANGELOG..."
for README in README.md .trae/skills/image-gen-bridge/README.md; do
    sed -i "/^### v$CURRENT_VERSION$/c\### v$NEW_VERSION\n- 🚀 Release v$NEW_VERSION" "$README"
done
echo "   Done."

echo ""
echo "[4/5] Committing changes..."
git add .
git commit -m "chore: bump version to v$NEW_VERSION"
echo "   Done."

echo ""
echo "[5/5] Creating and pushing tag..."
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
git push origin HEAD
git push origin "v$NEW_VERSION"
echo "   Done."

echo ""
echo "========================================="
echo "  Release v$NEW_VERSION completed!"
echo "========================================="
echo ""
echo "Changes:"
echo "  - VERSION: $CURRENT_VERSION -> $NEW_VERSION"
echo "  - README.md: Updated version references"
echo "  - Git tag: v$NEW_VERSION"
echo ""
