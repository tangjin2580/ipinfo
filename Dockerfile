# 第一阶段：构建 Python 应用
FROM debian:bullseye AS python_builder


# 更新和安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-venv \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到工作目录
COPY requirements.txt ./requirements.txt

# 创建并激活虚拟环境，安装依赖
RUN python3 -m venv venv \
    && ./venv/bin/pip install --upgrade pip \
    && ./venv/bin/pip install -r requirements.txt \
    && ./venv/bin/pip install gunicorn \
    && ls -al ./venv/bin  # 确认 Gunicorn 是否存在

# 复制 Flask 应用文件
COPY server/app.py ./app.py

# 暴露端口
EXPOSE 8080

# 启动 Gunicorn，指向虚拟环境中的 Flask 应用
CMD ["./venv/bin/gunicorn", "app:app", "-b", "0.0.0.0:8080", "--workers", "4", "--pid", "gunicorn.pid"]

# 第二阶段：构建 Vue 应用
FROM node:14 AS vue_builder


RUN npm cache clean --force


# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json 到容器中
COPY ipinfo-web/package.json ipinfo-web/package-lock.json ./

# 复制其余的项目文件到容器中
COPY ipinfo-web/ ./

# 安装依赖
RUN npm install --verbose

# 构建 Vue 应用
RUN npm run build --verbose

# 确保 dist 目录存在
RUN ls -al dist && pwd

# 第三阶段：使用 Nginx 提供服务
FROM nginx:alpine AS nginx_builder

# 复制打包好的 Vue 应用到 Nginx 目录
COPY --from=vue_builder /app/dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
