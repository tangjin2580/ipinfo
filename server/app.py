from flask import Flask, jsonify
from flask_cors import CORS
import requests
import dns.resolver  # 使用 dnspython 进行域名解析
import os
import logging  # 添加日志模块
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 从环境变量获取 Token
TOKEN = os.getenv('IPINFO_TOKEN')


@app.route('/api/ipinfo/<string:input>', methods=['GET'])
def ip_info(input):
    logger.info(f'Querying information for: {input}')  # 日志信息
    try:
        # 存储最终返回的数据
        all_ip_info = []

        # 检查输入是否为有效的 IP 地址
        if input.count('.') == 3:  # 简单判断是否为 IP 地址
            ips = [input]  # 将其视为有效 IP
        else:
            # 如果是域名，解析获取 IP 地址
            resolved_ip_data = resolve_domain(input)  # 解析域名
            logger.info(f'Resolved {input} to IP data: {resolved_ip_data}')  # 记录解析结果
            if resolved_ip_data and 'ip' in resolved_ip_data:
                ips = resolved_ip_data['ip']  # 获取所有解析到的 IP 地址
            else:
                return jsonify({'error': '无法解析域名'}), 400

        # 用每个 IP 地址获取 IP 信息
        for ip in ips:
            response = requests.get(f'https://ipinfo.io/{ip}/json?token={TOKEN}')
            response.raise_for_status()  # 确保请求没有错误
            data = response.json()  # 解析 JSON 数据
            logger.info(f'Successfully retrieved info for {ip}: {data}')  # 成功日志
            all_ip_info.append(data)  # 将每个 IP 的信息添加到列表中

        return jsonify(all_ip_info)  # 返回所有 IP 信息列表
    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching info for {input}: {str(e)}')  # 错误日志
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {e}')  # 捕获其他意外错误
        return jsonify({'error': '内部服务器错误'}), 500


@app.route('/api/resolve/<string:domain>', methods=['GET'])
def resolve_domain(domain):
    logger.info(f'Attempting to resolve domain: {domain}')  # 日志信息
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['114.114.114.114']  # 使用指定的 DNS 服务器
        answers = resolver.resolve(domain, 'A')  # 查询 A 记录
        ips = [str(answer) for answer in answers]  # 获取 IP 地址
        if ips:
            logger.info(f'Resolved {domain} to IP(s): {ips}')  # 成功日志
            return {'ip': ips}  # 返回域名及解析到的 IP 地址，保持为字典
        else:
            return jsonify({'error': '未找到解析结果'}), 404
    except Exception as e:
        logger.error(f'Error while resolving domain {domain}: {str(e)}')  # 错误日志
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # 启动 Flask 应用
