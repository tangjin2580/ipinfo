#!/bin/bash
set -euo pipefail

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Docker环境强制非交互apt
export DEBIAN_FRONTEND=noninteractive
export DEBIAN_PRIORITY=critical

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  IPinfo DNS 解析系统启动脚本(Docker版)${NC}"
echo -e "${BLUE}========================================${NC}"

# 安装lsof
if ! command -v lsof &> /dev/null; then
    echo -e "${YELLOW}⚠️  lsof 未安装，正在非交互安装...${NC}"
    if command -v apt &> /dev/null; then
        apt update -qq && apt install -y -qq lsof && rm -rf /var/lib/apt/lists/*
    elif command -v yum &> /dev/null; then
        yum install -y -q lsof && yum clean all
    fi
fi

# 检查虚拟环境
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${RED}📦 虚拟环境不存在，正在创建...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    
    # 升级pip
    echo -e "${YELLOW}📦 升级pip...${NC}"
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
    
    # 安装依赖 - 修正路径到 server/requirements.txt
    if [ -f "$SCRIPT_DIR/server/requirements.txt" ]; then
        echo -e "${GREEN}📦 安装后端依赖...${NC}"
        pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r "$SCRIPT_DIR/server/requirements.txt"
    else
        echo -e "${YELLOW}⚠️ server/requirements.txt 不存在，安装基础依赖...${NC}"
        pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple flask flask-cors gunicorn python-dotenv requests dnspython
    fi
else
    source "$SCRIPT_DIR/venv/bin/activate" || { echo -e "${RED}❌ 无法激活虚拟环境${NC}"; exit 1; }
fi

# 检查核心依赖
if ! python3 -c "import dotenv" &> /dev/null; then
    echo -e "${YELLOW}⚠️ python-dotenv 未安装，手动补装...${NC}"
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple python-dotenv
fi
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}⚠️ gunicorn 未安装，正在安装...${NC}"
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple gunicorn
fi

# 端口检测函数
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}❌ 端口 $1 已被占用${NC}"
        return 1
    fi
    return 0
}

# 启动前端服务（后台运行）
start_frontend() {
    if [ -d "$SCRIPT_DIR/dns-compare-tool" ]; then
        echo -e "\n${GREEN}🌐 启动前端服务...${NC}"
        cd "$SCRIPT_DIR/dns-compare-tool" || return
        
        FRONTEND_PORT=3000
        if ! check_port 3000; then
            FRONTEND_PORT=3001
        fi
        
        # 检查是否有 index.html
        if [ -f "index.html" ]; then
            # 前端后台启动
            python3 -m http.server $FRONTEND_PORT &
            FRONTEND_PID=$!
            echo $FRONTEND_PID > "$SCRIPT_DIR/server/frontend.pid"
            echo -e "${GREEN}✅ 前端服务已启动 (http://0.0.0.0:$FRONTEND_PORT)${NC}"
        else
            echo -e "${YELLOW}⚠️ 前端目录中没有 index.html，跳过前端启动${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ 前端目录不存在，跳过前端启动${NC}"
    fi
}

# 启动后端服务
start_backend() {
    echo -e "\n${GREEN}🚀 启动后端服务...${NC}"
    
    # 检查端口
    if ! check_port 8080; then
        echo -e "${RED}❌ 端口 8080 被占用，无法启动后端${NC}"
        exit 1
    fi
    
    # 进入server目录
    cd "$SCRIPT_DIR/server" || { echo -e "${RED}❌ 无法进入 server 目录${NC}"; exit 1; }
    
    echo -e "${GREEN}✅ 后端服务即将启动 (http://0.0.0.0:8080)${NC}"
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ 所有服务启动完成，开始前台运行${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    # 启动gunicorn（前台运行，作为容器主进程）
    exec gunicorn app:app \
        --bind 0.0.0.0:8080 \
        --workers 4 \
        --pid gunicorn.pid \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        --capture-output
}

# 主函数
main() {
    # 启动前端（后台）
    start_frontend
    
    # 启动后端（前台，会阻塞）
    start_backend
}

# 执行主函数
main