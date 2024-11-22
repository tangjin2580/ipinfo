#!/bin/bash

# 读取 PID 文件并终止进程
if [ -f gunicorn.pid ]; then
    PID=$(cat gunicorn.pid)
    echo "关闭 Flask 应用程序 (PID: $PID)..."
    kill $PID
    rm gunicorn.pid  # 删除 PID 文件
else
    echo "没有找到运行的 Flask 应用程序。"
fi
