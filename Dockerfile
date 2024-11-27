FROM python:3.9-slim AS builder

# 更新和安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && apt-get clean

# 设置工作目录
WORKDIR /app

# 复制当前目录的内容到容器内的 /app 目录
COPY . .

# 安装依赖
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install pyinstaller

# 使用 PyInstaller 打包应用，确保路径没有问题
RUN pyinstaller --onefile --add-data "server/.env:." "server/app.py"  # 注意路径须正确且使用相对路径

# 使用 Nginx 作为基础镜像
FROM nginx:alpine

# 复制打包好的应用到 Nginx 目录
COPY --from=builder /app/dist/app /usr/share/nginx/html/app
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

