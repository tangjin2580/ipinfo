# 使用 Debian 作为基础镜像
FROM debian:bullseye

# 更换 Debian 的软件源为阿里云镜像（如果需要）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 设置时区
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

# 更新和安装系统依赖
RUN apt-get update && apt-get install -y \
    bash-completion \
    curl \
    vim \
    build-essential \
    python3 \
    python3-venv \
    python3-pip \
    git \
    wget \
    unzip \
    nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 克隆后端代码
RUN git clone https://gitee.com/tang9999/ipinfo.git .
RUN git checkout index  # 切换到最新分支

# 安装后端依赖
RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt \
    && pip3 install gunicorn
# 创建目标目录
RUN mkdir -p /usr/share/nginx/html/

# 下载并解压前端构建包
RUN wget https://github.com/tangjin2580/ipinfo-web/releases/latest/download/dist.zip \
    && unzip dist.zip -d /usr/share/nginx/html \
    && mv /usr/share/nginx/html/dist/* /usr/share/nginx/html/ \
    && rm -rf /usr/share/nginx/html/dist \
    && rm dist.zip

# 复制 nginx.conf 到 Nginx 配置目录
RUN cd /app/docker \
    && cp nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
# 启动 Gunicorn 和 Nginx
CMD ["bash", "-c", "cd /app/server && gunicorn app:app -b 0.0.0.0:8080 --workers 4 --pid gunicorn.pid & nginx -g 'daemon off;'"]

