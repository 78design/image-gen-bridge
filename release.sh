#!/bin/bash

set -e

echo "当前版本: $(cat VERSION)"
echo "升级到: 1.3.0"
echo ""

echo "1. 更新 VERSION 文件..."
echo "1.3.0" > VERSION
echo "1.3.0" > .trae/skills/image-gen-bridge/VERSION

echo "2. 更新 README..."
sed -i.bak "s/v1\.2\.0/v1.3.0/g" README.md
sed -i.bak "s/v1\.2\.0/v1.3.0/g" .trae/skills/image-gen-bridge/README.md
rm -f *.bak .trae/skills/image-gen-bridge/*.bak

echo "3. Git 提交..."
git config --global user.email "trae@example.com"
git config --global user.name "Trae AI"
git add -A
git commit -m "版本更新：v1.3.0"
git tag -a v1.3.0 -m "Release v1.3.0"

echo "4. 推送到远程..."
git push origin main
git push origin v1.3.0

echo ""
echo "🎉 v1.3.0 发布成功！"
echo "下载链接: https://github.com/78design/image-gen-bridge/releases/download/v1.3.0/image-gen-bridge-v1.3.0.zip"
