#!/bin/bash
# image-gen-bridge - Automated Release Script
# Usage: ./release.sh <new_version>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <new_version>"
    echo "Example: $0 1.9.0"
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
echo "[1/4] Updating VERSION file..."
echo "$NEW_VERSION" > VERSION
echo "   Done."

echo ""
echo "[2/4] Updating README.md and SKILL.md..."
for FILE in README.md SKILL.md; do
    sed -i "s/v$CURRENT_VERSION/v$NEW_VERSION/g" "$FILE"
    sed -i "s/image-gen-bridge-v$CURRENT_VERSION/image-gen-bridge-v$NEW_VERSION/g" "$FILE"
done
echo "   Done."

echo ""
echo "[3/4] Committing changes..."
git add .
git commit -m "chore: bump version to v$NEW_VERSION"
echo "   Done."

echo ""
echo "[4/4] Creating and pushing tag..."
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
git push origin HEAD
git push origin "v$NEW_VERSION"
echo "   Done."

echo ""
echo "========================================="
echo "  Release v$NEW_VERSION completed!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Run ./build.sh to generate release zip"
echo "  2. Upload zip to GitHub Release page"
echo ""
