from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import dns.resolver  # 使用 dnspython 进行域名解析
import os
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 从环境变量获取 Token
TOKEN = os.getenv('IPINFO_TOKEN')


@app.route('/api/ipinfo/<string:input>', methods=['GET'])
def ip_info(input):
    logger.info(f'Querying information for: {input}')
    try:
        all_ip_info = []
        dns_server = request.args.get('dns', '114.114.114.114')
        logger.info(f'Received DNS server（1.收到的dns）: {dns_server}')  # 记录收到的 DNS 服务器

        ips = [input] if input.count('.') == 3 else resolve_domain(input, dns_server)

        if not ips:
            logger.warn(f'Failed to resolve domain: {input} with DNS: {dns_server}')  # 记录解析失败的情况
            return jsonify({'error': '无法解析域名'}), 400

        logger.info(f'Resolved IP(s): {ips} for input: {input}')  # 记录解析结果

        for ip in ips:
            data = get_ip_info(ip)
            if data is not None:
                all_ip_info.append(data)

        if not all_ip_info:
            logger.warn(f'No data found for IP(s): {ips}')  # 无数据的记录
            return jsonify({'error': '未找到相关信息'}), 404

        return jsonify(all_ip_info)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return jsonify({'error': '内部服务器错误'}), 500


def get_ip_info(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json?token={TOKEN}')
        response.raise_for_status()
        data = response.json()
        logger.info(f'Successfully retrieved info for {ip}: {data}')
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching info for {ip}: {str(e)}')
        return None


def resolve_domain(domain, dns_server='114.114.114.114'):
    logger.info(f'Attempting to resolve domain: {domain} using DNS: {dns_server}')
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]

        logger.info(f'Setting resolver nameserver to: {dns_server}')  # 记录设置的 DNS 服务器
        answers = resolver.resolve(domain, 'A')
        ips = [str(answer) for answer in answers]
        logger.info(f'Resolved {domain} to IP(s): {ips}')
        return ips
    except Exception as e:
        logger.error(f'Error while resolving domain {domain}: {str(e)}')
        return []


@app.route('/api/resolve/<string:domain>', methods=['GET'])
def resolve_domain_api(domain):
    dns_server = request.args.get('dns', default='114.114.114.114')
    logger.info('Resolving domain: {domain} using DNS: {dns_server}')  # 记录解析请求
    ips = resolve_domain(domain, dns_server)
    if ips:
        return {'ip': ips}
    logger.warn(f'Failed to resolve domain: {domain} with DNS: {dns_server}')  # 记录解析失败
    return jsonify({'error': '未找到解析结果'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
