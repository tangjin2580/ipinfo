#!/bin/bash
cd /opt/ipinfo-main

# 激活虚拟环境
source venv/bin/activate

cd /opt/ipinfo-main/server/
# 启动 Flask 应用程序使用 Gunicorn
echo "启动 Flask 应用程序..."
gunicorn app:app -b 0.0.0.0:8080 --workers 4 --pid gunicorn.pid &
