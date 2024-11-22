#!/bin/bash

# 检查是否在正确的目录中
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python -m venv venv  # 创建虚拟环境
    echo "虚拟环境 'venv' 创建完成。"
else
    echo "虚拟环境 'venv' 已存在。"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装库依赖
echo "安装依赖库..."
pip install Flask Flask-CORS requests dnspython python-dotenv

# 生成 requirements.txt
pip freeze > requirements.txt
echo "依赖库已安装，并已生成 requirements.txt"

# 提示用户
echo "全部设置完成！您可以通过运行 'source venv/bin/activate' 来激活虚拟环境。"
