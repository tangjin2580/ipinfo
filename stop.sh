#!/bin/bash

# 读取 PID 文件并终止进程
if [ -f gunicorn.pid ]; then
    PID=$(cat gunicorn.pid)

    # 检查进程是否存在
    if ps -p "$PID" > /dev/null; then
        echo "关闭 Flask 应用程序 (PID: $PID)..."
        kill "$PID"

        # 等待进程结束
        if wait "$PID"; then
            echo "Flask 应用程序已成功关闭。"
        else
            echo "关闭 Flask 应用程序失败，尝试强制终止..."
            kill -9 "$PID" || { echo "强制终止失败，PID: $PID 不存在或无法关闭."; exit 1; }
        fi

        # 删除 PID 文件
        rm -f gunicorn.pid
        echo "已删除 PID 文件。"
    else
        echo "进程 $PID 不存在，无法关闭。"
        rm -f gunicorn.pid  # 删除 PID 文件
    fi
else
    echo "没有找到运行的 Flask 应用程序。"
fi
