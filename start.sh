#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  IPinfo DNS 解析系统启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查虚拟环境
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${RED}❌ 虚拟环境不存在，正在创建...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    source "$SCRIPT_DIR/venv/bin/activate" || { echo -e "${RED}❌ 无法激活虚拟环境${NC}"; exit 1; }
fi

# 检查依赖
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}⚠️  gunicorn 未安装，正在安装...${NC}"
    pip install gunicorn
fi

# 进入服务器目录
cd "$SCRIPT_DIR/server" || { echo -e "${RED}❌ 无法进入 server 目录${NC}"; exit 1; }

# 检查端口占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  端口 $1 已被占用${NC}"
        return 1
    fi
    return 0
}

# 启动后端服务
echo -e "\n${GREEN}🚀 启动后端服务...${NC}"
if ! check_port 8080; then
    echo -e "${RED}❌ 端口 8080 被占用，请先停止相关进程${NC}"
    echo -e "${YELLOW}💡 提示: 运行 ./stop.sh 停止现有服务${NC}"
    exit 1
fi

gunicorn app:app -b 0.0.0.0:8080 --workers 4 --pid gunicorn.pid --daemon
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 后端服务已启动 (http://localhost:8080)${NC}"
else
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    exit 1
fi

# 启动前端服务
echo -e "\n${GREEN}🌐 启动前端服务...${NC}"
cd "$SCRIPT_DIR/dns-compare-tool" || { echo -e "${RED}❌ 无法进入前端目录${NC}"; exit 1; }

if ! check_port 3000; then
    echo -e "${YELLOW}⚠️  端口 3000 被占用，尝试使用端口 3001...${NC}"
    FRONTEND_PORT=3001
else
    FRONTEND_PORT=3000
fi

# 启动 Python 简单 HTTP 服务器
python3 -m http.server $FRONTEND_PORT > /dev/null 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$SCRIPT_DIR/server/frontend.pid"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 前端服务已启动 (http://localhost:$FRONTEND_PORT)${NC}"
else
    echo -e "${RED}❌ 前端服务启动失败${NC}"
    exit 1
fi

# 等待服务完全启动
echo -e "\n${BLUE}⏳ 等待服务启动...${NC}"
sleep 2

# 打开浏览器
echo -e "\n${GREEN}🌍 正在打开浏览器...${NC}"
FRONTEND_URL="http://localhost:$FRONTEND_PORT"

# 根据操作系统选择打开方式
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$FRONTEND_URL"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open "$FRONTEND_URL"
    elif command -v gnome-open &> /dev/null; then
        gnome-open "$FRONTEND_URL"
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    start "$FRONTEND_URL"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 服务启动成功！${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}后端 API:${NC}    http://localhost:8080"
echo -e "${GREEN}前端页面:${NC}    http://localhost:$FRONTEND_PORT"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}停止服务:${NC}    ./stop.sh"
echo -e "${YELLOW}查看日志:${NC}    tail -f log/app.log"
echo -e "${BLUE}========================================${NC}\n"
