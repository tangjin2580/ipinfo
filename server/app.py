from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import dns.resolver
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from country_mapping import get_country_name  # 字典映射
from cachetools import TTLCache
from datetime import datetime
import json

# 加载环境变量
load_dotenv()

# 创建时间戳
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file_path = f'../log/app_{timestamp}.log'  # 日志文件保存在上级目录，并加上时间戳

# 设置日志文件路径以及分割配置
handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# 设置根日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

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

# 初始化缓存，设置最大容量和有效期（一天）
cache = TTLCache(maxsize=1000, ttl=86400)  # 86400 秒 = 1 天


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

    # 新增变量用于存储解析的域名
    history_domain = input if input.count('.') != 3 else None

    # 检查缓存
    for ip in ips:
        if ip in cache:
            logger.info(f'Fetching {ip} from cache')
            all_ip_info.append(cache[ip])
        else:
            # 使用线程池并行查询 IP 信息
            futures = {executor.submit(get_ip_info, ip): ip for ip in ips if ip not in cache}

            for future in futures:
                ip = futures[future]
                try:
                    data = future.result()
                    if data is not None:
                        all_ip_info.append(data)
                        cache[ip] = data  # 将结果存入缓存
                        logger.info(f'Cached data for {ip}: {data}')  # 缓存成功的日志

                        # 如果是通过域名查询的，记录域名
                        if history_domain:
                            country_code = data.get('country')
                            country_name = get_country_name(country_code)  # 获取中文国家名称
                            save_query_history(history_domain, ip, dns_server, country_name)

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

        # 使用映射函数获取中文国家名称
        country_code = data.get('country')
        data['country'] = get_country_name(country_code)  # 替换为中文名称

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


# 历史记录文件路径
history_file_path = '../log/query_history.json'


# 保存查询历史记录
def save_query_history(domain, ip, dns_server, country):
    query_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    history_entry = {
        'domain': domain,
        'ip': ip,
        'dns': dns_server,
        'country': country,
        'timestamp': query_time
    }

    # 尝试读取已有历史记录
    try:
        if os.path.exists(history_file_path):
            with open(history_file_path, 'r') as f:
                history = json.load(f)
        else:
            history = []

        # 添加新的记录
        history.append(history_entry)

        # 保存到文件
        with open(history_file_path, 'w') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

        logger.info(f'Saved query history: {history_entry}')
    except Exception as e:
        logger.error(f'Error saving query history: {str(e)}')


@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        if os.path.exists(history_file_path):
            with open(history_file_path, 'r') as f:
                history = json.load(f)
            return jsonify(history)
        else:
            return jsonify([])  # 如果没有历史记录，返回空列表
    except Exception as e:
        logger.error(f'Error reading query history: {str(e)}')
        return jsonify({'error': '读取历史记录失败'}), 500


@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    cache.clear()
    logger.info('Cache has been cleared.')
    return jsonify({'message': '缓存已清理'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
