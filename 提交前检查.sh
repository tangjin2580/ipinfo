#!/bin/bash

echo "====================================================================="
echo "📋 提交前检查清单"
echo "====================================================================="
echo ""

# 检查关键文件
echo "1️⃣ 检查关键文件..."
files=(
    "README.md"
    "requirements.txt"
    ".gitignore"
    "server/app.py"
    "server/city_mapping.py"
    "server/country_mapping.py"
    "server/log_manager.py"
    "docs/完整文档.md"
)

missing=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
        missing=$((missing + 1))
    fi
done

if [ $missing -gt 0 ]; then
    echo "   ❌ 缺失 $missing 个关键文件"
    exit 1
fi

echo ""
echo "2️⃣ 检查备份目录..."
if [ -d ".backup" ]; then
    backup_count=$(find .backup -type f | wc -l)
    echo "   ✅ 备份目录存在 ($backup_count 个文件已备份)"
else
    echo "   ⚠️  备份目录不存在"
fi

echo ""
echo "3️⃣ 检查系统临时文件..."
ds_store=$(find . -name ".DS_Store" 2>/dev/null | wc -l)
pycache=$(find . -name "__pycache__" 2>/dev/null | wc -l)

if [ "$ds_store" -eq 0 ] && [ "$pycache" -eq 0 ]; then
    echo "   ✅ 无系统临时文件"
else
    echo "   ⚠️  发现 $ds_store 个.DS_Store, $pycache 个__pycache__"
fi

echo ""
echo "4️⃣ Git状态..."
if command -v git &> /dev/null; then
    echo "   当前分支: $(git branch --show-current)"
    echo "   未跟踪文件数: $(git status --short | grep '^??' | wc -l)"
    echo "   已修改文件数: $(git status --short | grep '^ M' | wc -l)"
    echo "   已暂存文件数: $(git status --short | grep '^M' | wc -l)"
fi

echo ""
echo "====================================================================="
echo "✅ 检查完成！项目可以提交"
echo "====================================================================="
echo ""
echo "📝 建议的提交命令:"
echo "   git add ."
echo "   git commit -m '重构: 项目结构标准化与文档整合'"
echo "   git push origin main"
echo ""
