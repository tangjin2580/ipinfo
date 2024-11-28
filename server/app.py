from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import dns.resolver
import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# 加载环境变量
load_dotenv()

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 初始化 Limiter
limiter = Limiter(
    get_remote_address,
    default_limits=["400 per minute", "50000 per month"]
)
app.config["LIMITER"] = limiter

# 从环境变量获取 Token
TOKEN = os.getenv('IPINFO_TOKEN')

# 使用线程池最大工作线程数
executor = ThreadPoolExecutor(max_workers=5)


@app.route('/api/ipinfo/<string:input>', methods=['GET'])
@limiter.limit("400 per minute")  # 每分钟限制 400 次请求
def ip_info(input):
    logger.info(f'Querying information for: {input}')
    all_ip_info = []
    dns_server = request.args.get('dns', '114.114.114.114')
    logger.info(f'Received DNS server: {dns_server}')

    # 判断输入是域名还是 IP 地址
    ips = [input] if input.count('.') == 3 else resolve_domain(input, dns_server)

    if not ips:
        logger.warning(f'Failed to resolve domain: {input} with DNS: {dns_server}')
        return jsonify({'error': '无法解析域名'}), 400

    logger.info(f'Resolved IP(s): {ips} for input: {input}')

    # 使用线程池并行查询 IP 信息
    futures = {executor.submit(get_ip_info, ip): ip for ip in ips}
    for future in futures:
        ip = futures[future]
        try:
            data = future.result()
            if data is not None:
                all_ip_info.append(data)
        except Exception as e:
            logger.error(f'Error fetching info for {ip}: {str(e)}')

    if not all_ip_info:
        logger.warning(f'No data found for IP(s): {ips}')
        return jsonify({'error': '未找到相关信息'}), 404

    return jsonify(all_ip_info)


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
        logger.info(f'Setting resolver nameserver to: {dns_server}')
        answers = resolver.resolve(domain, 'A')
        ips = [str(answer) for answer in answers]
        logger.info(f'Resolved {domain} to IP(s): {ips}')
        return ips
    except Exception as e:
        logger.error(f'Error while resolving domain {domain}: {str(e)}')
        return []


@app.route('/api/resolve/<string:domain>', methods=['GET'])
@limiter.limit("400 per minute")  # 每分钟限制 400 次请求
def resolve_domain_api(domain):
    dns_server = request.args.get('dns', default='114.114.114.114')
    logger.info(f'Resolving domain: {domain} using DNS: {dns_server}')
    ips = resolve_domain(domain, dns_server)
    if ips:
        return {'ip': ips}
    logger.warning(f'Failed to resolve domain: {domain} with DNS: {dns_server}')
    return jsonify({'error': '未找到解析结果'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
