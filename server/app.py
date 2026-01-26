from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import dns.resolver
import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from country_mapping import get_country_name
from city_mapping import get_city_name
from cachetools import TTLCache
from datetime import datetime
import json
import maxminddb
from log_manager import setup_logger, archive_old_logs, cleanup_empty_logs

# 加载环境变量
load_dotenv()

# 设置日志目录
log_dir = '../log'

# 使用优化的日志配置
logger = setup_logger(log_dir=log_dir)

# 启动时清理和归档旧日志
logger.info('🧹 正在清理旧日志...')
cleanup_empty_logs(log_dir)
archive_old_logs(log_dir, days=7)  # 归档7天前的日志

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    get_remote_address,
    default_limits=["400 per minute", "50000 per month"]
)
app.config["LIMITER"] = limiter

TOKEN = os.getenv('IPINFO_TOKEN')

# 多数据库支持
DB_DIR = os.path.join(os.path.dirname(__file__), 'db')
mmdb_databases = {}

# 加载所有可用的MMDB数据库
db_files = {
    'ipinfo': 'ipinfo_lite.mmdb',
    'geolite2': 'GeoLite2-City.mmdb',
    'ip2location': 'IP2LOCATION-LITE.mmdb'
}

for db_name, db_file in db_files.items():
    db_path = os.path.join(DB_DIR, db_file)
    try:
        if os.path.exists(db_path):
            mmdb_databases[db_name] = maxminddb.open_database(db_path)
            logger.info(f'✅ 加载数据库: {db_name} ({db_file})')
    except Exception as e:
        logger.warning(f'⚠️  无法加载 {db_name}: {str(e)}')

if not mmdb_databases:
    logger.warning('⚠️  未找到任何本地MMDB数据库，将仅使用在线API')

# 线程池
executor = ThreadPoolExecutor(max_workers=20, thread_name_prefix='ip-worker')

# 缓存
cache = TTLCache(maxsize=2000, ttl=86400)

# 统计
stats = {
    'local_queries': 0,
    'api_queries': 0,
    'cache_hits': 0,
    'total_queries': 0,
    'db_hits': {db_name: 0 for db_name in db_files.keys()}
}


@app.route('/api/ipinfo/<string:input>', methods=['GET'])
@limiter.limit("400 per minute")
def ip_info(input):
    logger.info(f'Querying information for: {input}')
    all_ip_info = []
    dns_server = request.args.get('dns', '114.114.114.114')

    ips = [input] if input.count('.') == 3 else resolve_domain(input, dns_server)

    if not ips:
        return jsonify({'error': '无法解析域名'}), 400

    history_domain = input if input.count('.') != 3 else None

    for ip in ips:
        if ip in cache:
            logger.info(f'🔄 从缓存获取: {ip}')
            stats['cache_hits'] += 1
            all_ip_info.append(cache[ip])
        else:
            data = get_ip_info(ip)
            if data:
                all_ip_info.append(data)
                cache[ip] = data

                if history_domain:
                    save_query_history(
                        history_domain, ip, dns_server, 
                        data.get('country'), data.get('city')
                    )

    if not all_ip_info:
        return jsonify({'error': '未找到相关信息'}), 404

    return jsonify(all_ip_info)


def get_ip_info_from_ipinfo_db(ip, reader):
    """从IPinfo格式的MMDB查询"""
    try:
        response = reader.get(ip)
        if not response:
            return None
        
        country_code = response.get('country')
        city_name = response.get('city')
        
        return {
            'ip': ip,
            'city': get_city_name(city_name) if city_name else '',
            'region': response.get('region', ''),
            'country': get_country_name(country_code) if country_code else '',
            'loc': response.get('loc', ''),
            'postal': response.get('postal', ''),
            'timezone': response.get('timezone', ''),
            'org': response.get('org', ''),
            'source': 'local:ipinfo'
        }
    except:
        return None


def get_ip_info_from_geolite2_db(ip, reader):
    """从GeoLite2格式的MMDB查询"""
    try:
        response = reader.get(ip)
        if not response:
            return None
        
        # GeoLite2的数据结构
        country_code = response.get('country', {}).get('iso_code')
        city_name = response.get('city', {}).get('names', {}).get('en')
        location = response.get('location', {})
        
        return {
            'ip': ip,
            'city': get_city_name(city_name) if city_name else '',
            'region': response.get('subdivisions', [{}])[0].get('names', {}).get('en', '') if response.get('subdivisions') else '',
            'country': get_country_name(country_code) if country_code else '',
            'loc': f"{location.get('latitude', '')},{location.get('longitude', '')}" if location.get('latitude') else '',
            'postal': response.get('postal', {}).get('code', ''),
            'timezone': location.get('time_zone', ''),
            'source': 'local:geolite2'
        }
    except:
        return None


def get_ip_info_from_mmdb(ip):
    """
    从本地MMDB数据库查询（多数据源支持）
    查询优先级：ipinfo > geolite2 > ip2location
    """
    if not mmdb_databases:
        return None
    
    # 按优先级尝试各个数据库
    for db_name, reader in mmdb_databases.items():
        try:
            if db_name == 'ipinfo':
                data = get_ip_info_from_ipinfo_db(ip, reader)
            elif db_name == 'geolite2':
                data = get_ip_info_from_geolite2_db(ip, reader)
            else:
                # 其他数据库的通用读取
                response = reader.get(ip)
                if response:
                    data = {
                        'ip': ip,
                        'country': get_country_name(response.get('country')),
                        'city': get_city_name(response.get('city')),
                        'source': f'local:{db_name}'
                    }
                else:
                    data = None
            
            if data and data.get('city'):  # 确保有城市信息
                stats['db_hits'][db_name] += 1
                logger.info(f'💾 本地查询成功 [{db_name}]: {ip} -> {data.get("city")}')
                stats['local_queries'] += 1
                return data
                
        except Exception as e:
            logger.debug(f'{db_name} 查询失败: {str(e)}')
            continue
    
    return None


def get_ip_info_from_api(ip, timeout=5):
    """从ipinfo.io API查询"""
    try:
        response = requests.get(
            f'https://ipinfo.io/{ip}/json?token={TOKEN}',
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        
        country_code = data.get('country')
        if country_code:
            data['country'] = get_country_name(country_code)
        
        city_name = data.get('city')
        if city_name:
            data['city'] = get_city_name(city_name)
        
        data['source'] = 'api'
        
        logger.info(f'🌐 API查询成功: {ip} -> {data.get("city")}')
        stats['api_queries'] += 1
        return data
        
    except:
        return None


def get_ip_info(ip, timeout=5):
    """
    获取IP信息（多数据源策略）
    
    查询顺序：
    1. 缓存
    2. 本地MMDB数据库（多个，按优先级）
    3. 在线API
    """
    stats['total_queries'] += 1
    
    # 尝试本地MMDB
    local_data = get_ip_info_from_mmdb(ip)
    if local_data:
        return local_data
    
    # 降级到API
    api_data = get_ip_info_from_api(ip, timeout)
    if api_data:
        return api_data
    
    return {
        'ip': ip,
        'city': '',
        'country': '',
        'source': 'none'
    }


def resolve_domain(domain, dns_server='114.114.114.114', timeout=5):
    """DNS解析"""
    logger.info(f'Resolving: {domain} via {dns_server}')
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = timeout
        resolver.lifetime = timeout
        answers = resolver.resolve(domain, 'A')
        ips = [str(answer) for answer in answers]
        logger.info(f'Resolved {domain} to: {ips}')
        return ips
    except:
        return []


@app.route('/api/resolve/<string:domain>', methods=['GET'])
@limiter.limit("400 per minute")
def resolve_domain_api(domain):
    dns_server = request.args.get('dns', default='114.114.114.114')
    ips = resolve_domain(domain, dns_server)
    if ips:
        return jsonify({'ip': ips})
    return jsonify({'error': '未找到解析结果'}), 404


history_file_path = os.path.join(log_dir, 'query_history.json')


def save_query_history(domain, ip, dns_server, country, city):
    """保存历史"""
    query_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    history_entry = {
        'domain': domain,
        'ip': ip,
        'dns': dns_server,
        'country': country,
        'city': city,
        'timestamp': query_time
    }

    try:
        if os.path.exists(history_file_path):
            with open(history_file_path, 'r') as f:
                history = json.load(f)
        else:
            history = []

        history.append(history_entry)

        with open(history_file_path, 'w') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f'Error saving history: {str(e)}')


@app.route('/api/batch-query', methods=['POST'])
@limiter.limit("200 per minute")
def batch_query():
    """批量查询"""
    try:
        request_data = request.get_json()
        if not request_data or 'domains' not in request_data or 'dns_servers' not in request_data:
            return jsonify({'error': '请求格式错误'}), 400

        domains = request_data['domains']
        dns_servers = request_data['dns_servers']

        all_results = []
        future_to_task = {}
        
        for domain in domains:
            for dns_server in dns_servers:
                future = executor.submit(query_domain_for_country, domain, dns_server)
                future_to_task[future] = (domain, dns_server)

        for future in as_completed(future_to_task, timeout=60):
            try:
                result = future.result(timeout=1)
                if result:
                    all_results.extend(result)
            except:
                pass

        logger.info(f'📊 Batch query: {len(all_results)} results')
        return jsonify(all_results)

    except Exception as e:
        logger.error(f'Batch query error: {str(e)}')
        return jsonify({'error': '批量查询失败'}), 500


def query_domain_for_country(domain, dns_server):
    """单域名查询"""
    try:
        ips = resolve_domain(domain, dns_server, timeout=5)
        if ips:
            result = []
            for ip in ips:
                data = get_ip_info(ip, timeout=5)
                if data:
                    result.append({
                        'domain': domain,
                        'ip': ip,
                        'dns': dns_server,
                        'country': data.get('country'),
                        'city': data.get('city'),
                        'source': data.get('source', 'unknown')
                    })
            return result
        return None
    except:
        return None


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取历史"""
    try:
        if os.path.exists(history_file_path):
            with open(history_file_path, 'r') as f:
                history = json.load(f)
            return jsonify(history)
        return jsonify([])
    except:
        return jsonify({'error': '读取失败'}), 500


@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """清除缓存"""
    cache.clear()
    return jsonify({'message': '缓存已清理'}), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """统计信息"""
    return jsonify({
        'total_queries': stats['total_queries'],
        'local_queries': stats['local_queries'],
        'api_queries': stats['api_queries'],
        'cache_hits': stats['cache_hits'],
        'cache_size': len(cache),
        'local_hit_rate': f"{stats['local_queries'] / max(stats['total_queries'], 1) * 100:.2f}%",
        'api_hit_rate': f"{stats['api_queries'] / max(stats['total_queries'], 1) * 100:.2f}%",
        'databases': {
            'loaded': list(mmdb_databases.keys()),
            'hits': stats['db_hits']
        }
    })


if __name__ == '__main__':
    try:
        logger.info('🚀 Starting DNS resolution service...')
        logger.info(f'📚 Loaded databases: {list(mmdb_databases.keys())}')
        app.run(host='0.0.0.0', port=8080, debug=False)
    finally:
        for reader in mmdb_databases.values():
            reader.close()
