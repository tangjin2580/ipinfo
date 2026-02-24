    #!/bin/bash
    set -euo pipefail  # 严格模式：未定义变量/命令失败/管道失败都退出，且返回非0码

    # 颜色定义
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Docker环境强制非交互apt，解决debconf报错
    export DEBIAN_FRONTEND=noninteractive
    export DEBIAN_PRIORITY=critical

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  IPinfo DNS 解析系统启动脚本(Docker版)${NC}"
    echo -e "${BLUE}========================================${NC}"

    # 安装lsof（非交互模式，无任何弹窗）
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
        echo -e "${RED}❌ 虚拟环境不存在，正在创建...${NC}"
        python3 -m venv "$SCRIPT_DIR/venv"
        source "$SCRIPT_DIR/venv/bin/activate"
        # 升级pip+安装依赖，指定国内源加速（解决Docker网络慢）
        pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
        pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r "$SCRIPT_DIR/requirements.txt"
    else
        source "$SCRIPT_DIR/venv/bin/activate" || { echo -e "${RED}❌ 无法激活虚拟环境${NC}"; exit 1; }
    fi

    # 检查核心依赖（强制验证python-dotenv是否安装）
    if ! python3 -c "import dotenv" &> /dev/null; then
        echo -e "${YELLOW}⚠️  python-dotenv 未安装，手动补装...${NC}"
        pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple python-dotenv
    fi
    if ! command -v gunicorn &> /dev/null; then
        echo -e "${YELLOW}⚠️  gunicorn 未安装，正在安装...${NC}"
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

    # 启动后端服务
    echo -e "\n${GREEN}🚀 启动后端服务...${NC}"
    cd "$SCRIPT_DIR/server" || { echo -e "${RED}❌ 无法进入 server 目录${NC}"; exit 1; }
    if ! check_port 8080; then
        exit 1
    fi

    # 启动前端服务
    echo -e "\n${GREEN}🌐 启动前端服务...${NC}"
    cd "$SCRIPT_DIR/dns-compare-tool" || { echo -e "${RED}❌ 无法进入前端目录${NC}"; exit 1; }
        #!/bin/bash
    set -euo pipefail  # 严格模式：未定义变量/命令失败/管道失败都退出，且返回非0码

    # 颜色定义
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Docker环境强制非交互apt，解决debconf报错
    export DEBIAN_FRONTEND=noninteractive
    export DEBIAN_PRIORITY=critical

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  IPinfo DNS 解析系统启动脚本(Docker版)${NC}"
    echo -e "${BLUE}========================================${NC}"

    # 安装lsof（非交互模式，无任何弹窗）
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
        echo -e "${RED}❌ 虚拟环境不存在，正在创建...${NC}"
        python3 -m venv "$SCRIPT_DIR/venv"
        source "$SCRIPT_DIR/venv/bin/activate"
        # 升级pip+安装依赖，指定国内源加速（解决Docker网络慢）
        pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
        pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r "$SCRIPT_DIR/requirements.txt"
    else
        source "$SCRIPT_DIR/venv/bin/activate" || { echo -e "${RED}❌ 无法激活虚拟环境${NC}"; exit 1; }
    fi

    # 检查核心依赖（强制验证python-dotenv是否安装）
    if ! python3 -c "import dotenv" &> /dev/null; then
        echo -e "${YELLOW}⚠️  python-dotenv 未安装，手动补装...${NC}"
        pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple python-dotenv
    fi
    if ! command -v gunicorn &> /dev/null; then
        echo -e "${YELLOW}⚠️  gunicorn 未安装，正在安装...${NC}"
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

    # 启动后端服务
    echo -e "\n${GREEN}🚀 启动后端服务...${NC}"
    cd "$SCRIPT_DIR/server" || { echo -e "${RED}❌ 无法进入 server 目录${NC}"; exit 1; }
    if ! check_port 8080; then
        exit 1
    fi

    # 启动前端服务
    echo -e "\n${GREEN}🌐 启动前端服务...${NC}"
    cd "$SCRIPT_DIR/dns-compare-tool" || { echo -e "${RED}❌ 无法进入前端目录${NC}"; exit 1; }
    FRONTEND_PORT=3000
    if ! check_port 3000; then
        FRONTEND_PORT=3001
    fi
    # 前端后台启动，记录PID
    python3 -m http.server $FRONTEND_PORT &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$SCRIPT_DIR/server/frontend.pid"
    echo -e "${GREEN}✅ 前端服务已启动 (http://0.0.0.0:$FRONTEND_PORT)${NC}"

    # 前台启动后端（容器主进程），强制输出日志到stdout/stderr
    cd "$SCRIPT_DIR/server" || exit 1
    echo -e "${GREEN}✅ 后端服务即将启动 (http://0.0.0.0:8080)${NC}"
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ 所有服务启动完成，开始前台运行${NC}"
    echo -e "${BLUE}========================================${NC}\n"

    # 启动gunicorn，若失败返回非0码，让Docker检测到启动失败
    exec gunicorn app:app -b 0.0.0.0:8080 --workers 4 --pid gunicorn.pid --log-level info=3000
    if ! check_port 3000; then
        FRONTEND_PORT=3001
    fi
    # 前端后台启动，记录PID
    python3 -m http.server $FRONTEND_PORT &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$SCRIPT_DIR/server/frontend.pid"
    echo -e "${GREEN}✅ 前端服务已启动 (http://0.0.0.0:$FRONTEND_PORT)${NC}"

    # 前台启动后端（容器主进程），强制输出日志到stdout/stderr
    cd "$SCRIPT_DIR/server" || exit 1
    echo -e "${GREEN}✅ 后端服务即将启动 (http://0.0.0.0:8080)${NC}"
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ 所有服务启动完成，开始前台运行${NC}"
    echo -e "${BLUE}========================================${NC}\n"

    # 启动gunicorn，若失败返回非0码，让Docker检测到启动失败
    exec gunicorn app:app -b 0.0.0.0:8080 --workers 4 --pid gunicorn.pid --log-level info