#!/bin/bash

# 获取当前脚本所在的目录
# source venv/bin/activate
# pip install -r requirements.txt
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 激活虚拟环境
source "$SCRIPT_DIR/venv/bin/activate" || { echo "虚拟环境不存在"; exit 1; }

# 进入服务器目录
cd "$SCRIPT_DIR/server" || { echo "无法进入 server 目录"; exit 1; }

# 启动 Flask 应用程序使用 Gunicorn
echo "启动 Flask 应用程序..."
gunicorn app:app -b 0.0.0.0:8080 --workers 4 --pid gunicorn.pid &
