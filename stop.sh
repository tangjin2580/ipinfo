#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  IPinfo DNS 解析系统停止脚本${NC}"
echo -e "${BLUE}========================================${NC}"

cd "$SCRIPT_DIR/server" || { echo -e "${RED}❌ 无法进入 server 目录${NC}"; exit 1; }

# 停止后端服务
echo -e "\n${YELLOW}🛑 停止后端服务...${NC}"
if [ -f gunicorn.pid ]; then
    PID=$(cat gunicorn.pid)
    
    # 检查进程是否存在
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${BLUE}   进程 PID: $PID${NC}"
        kill "$PID"
        
        # 等待进程结束
        sleep 1
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}   正常关闭失败，尝试强制终止...${NC}"
            kill -9 "$PID" 2>/dev/null
        fi
        
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  进程 $PID 不存在${NC}"
    fi
    
    rm -f gunicorn.pid
else
    echo -e "${YELLOW}⚠️  未找到后端服务 PID 文件${NC}"
fi

# 停止前端服务
echo -e "\n${YELLOW}🛑 停止前端服务...${NC}"
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    
    # 检查进程是否存在
    if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
        echo -e "${BLUE}   进程 PID: $FRONTEND_PID${NC}"
        kill "$FRONTEND_PID"
        
        # 等待进程结束
        sleep 1
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}   正常关闭失败，尝试强制终止...${NC}"
            kill -9 "$FRONTEND_PID" 2>/dev/null
        fi
        
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  进程 $FRONTEND_PID 不存在${NC}"
    fi
    
    rm -f frontend.pid
else
    echo -e "${YELLOW}⚠️  未找到前端服务 PID 文件${NC}"
fi

# 额外清理：查找可能遗留的 Python HTTP 服务器进程
echo -e "\n${BLUE}🔍 检查是否有遗留的服务进程...${NC}"
LEFTOVER_PIDS=$(lsof -ti:8080,3000,3001 2>/dev/null)
if [ ! -z "$LEFTOVER_PIDS" ]; then
    echo -e "${YELLOW}⚠️  发现遗留进程，正在清理...${NC}"
    echo "$LEFTOVER_PIDS" | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ 遗留进程已清理${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo -e "${BLUE}========================================${NC}\n"
