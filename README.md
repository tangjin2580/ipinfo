# DNS解析与IP地理位置查询系统

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

一个高性能的DNS解析与IP地理位置查询系统，支持多DNS服务器批量查询、本地MMDB数据库优先查询、自动日志管理等功能。

## ✨ 核心特性

- 🌐 **多DNS服务器查询** - 支持同时查询多个DNS服务器并对比结果
- 🗺️ **IP地理位置信息** - 显示IP的国家、城市等地理信息（中文）
- ⚡ **本地数据库优先** - 支持IPinfo MMDB + MaxMind GeoLite2，本地命中率95%+
- 📊 **查询历史记录** - 自动保存查询历史，支持导出
- 🧵 **高并发处理** - ThreadPoolExecutor + 20线程并发
- 🗂️ **智能日志管理** - 自动轮转、压缩、归档，节省73%空间
- 🚀 **性能优化** - 缓存机制 + 超时控制，查询速度<100ms

## 🚀 快速开始

### 1. 安装依赖

```bash
cd server
pip3 install -r requirements.txt
```

### 2. 配置数据库（可选但推荐）

将MMDB数据库文件放置到 `server/db/` 目录：

- `ipinfo_lite.mmdb` - [获取方式](docs/完整文档.md#数据库获取)
- `GeoLite2-City.mmdb` - [获取方式](docs/完整文档.md#数据库获取)

> 💡 **不配置数据库也可运行**，但会完全依赖API调用（速度慢+有限额）

### 3. 启动服务

```bash
# 开发环境
python3 app.py

# 生产环境 (推荐)
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

服务运行在: `http://0.0.0.0:8080`

### 4. 访问前端

打开 `dns-compare-tool/index.html` 即可使用。

## 📖 完整文档

详细的配置说明、API文档、故障排查请查看：

📚 **[完整文档](docs/完整文档.md)**

包含内容：
- 系统架构与技术栈
- 数据库配置指南（IPinfo + GeoLite2）
- 日志管理系统说明
- 性能优化方案
- API接口文档
- 故障排查手册

## 🏗️ 项目结构

```
ipinfo/
├── server/                     # 后端服务
│   ├── app.py                  # 主应用
│   ├── city_mapping.py         # 城市中文映射 (200+)
│   ├── country_mapping.py      # 国家中文映射
│   ├── log_manager.py          # 日志管理模块
│   ├── cleanup_logs.py         # 日志清理工具
│   ├── requirements.txt        # Python依赖
│   └── db/                     # 数据库目录
│       ├── ipinfo_lite.mmdb
│       └── GeoLite2-City.mmdb
├── log/                        # 日志目录
│   ├── app.log                 # 当前日志
│   ├── app.log.*.gz            # 压缩归档
│   ├── archive/                # 长期归档
│   └── query_history.json      # 查询历史
├── dns-compare-tool/           # 前端工具
│   └── index.html
├── docs/                       # 文档目录
│   └── 完整文档.md
├── docker/                     # Docker配置
├── README.md
├── requirements.txt
├── start.sh
└── stop.sh
```

## 🔧 核心技术

- **后端框架**: Flask 2.0+
- **DNS解析**: dnspython
- **IP查询**: maxminddb + IPinfo API
- **并发处理**: ThreadPoolExecutor
- **缓存**: TTLCache (10分钟)
- **前端**: Vue 3 + Axios

## 📊 性能指标

| 指标 | 纯API模式 | 本地MMDB模式 |
|-----|----------|-------------|
| 查询速度 | 1-2秒 | <1ms (100倍提升) |
| 本地命中率 | 0% | 95%+ |
| API调用量 | 100% | <5% (减少95%) |
| 月度成本 | 高 | 低 |

## 🛠️ 常用命令

### 启动服务

```bash
# 前台运行
python3 server/app.py

# 后台运行
./start.sh

# 生产环境
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### 停止服务

```bash
./stop.sh
# 或
kill $(cat server/gunicorn.pid)
```

### 日志管理

```bash
# 查看日志统计
python3 server/cleanup_logs.py --stats-only

# 清理旧日志
python3 server/cleanup_logs.py --days 7

# 查看实时日志
tail -f log/app.log
```

## 🐳 Docker部署

### 快速拉取镜像

```bash
docker pull crpi-soc4lkdq4i3mrdfh.cn-chengdu.personal.cr.aliyuncs.com/mydokcer/ipinfo-flask
docker pull crpi-soc4lkdq4i3mrdfh.cn-chengdu.personal.cr.aliyuncs.com/mydokcer/ipinfo-nginx
```

### 构建并运行

```bash
# 构建镜像
docker build -t ipinfo-api .

# 运行容器
docker run -d -p 8080:8080 --name ipinfo-api ipinfo-api

# 或使用已发布镜像
docker run -d -p 80:80 --name ipinfo-app tangjin2580/ipinfo-app:latest
```

### 访问服务

- API接口: `http://localhost:8080/api/batch-query`
- 前端页面: `http://localhost:80/`

## 📡 API示例

### 批量DNS查询

**请求**:
```bash
curl -X POST http://localhost:8080/api/batch-query \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["baidu.com", "google.com"],
    "dns_servers": ["8.8.8.8", "114.114.114.114"]
  }'
```

**响应**:
```json
[
  {
    "domain": "baidu.com",
    "ip": "110.242.74.102",
    "dns": "8.8.8.8",
    "city": "石家庄",
    "country": "中国",
    "source": "local:ipinfo"
  }
]
```

完整API文档请查看: [docs/完整文档.md](docs/完整文档.md#api文档)

## 🔍 故障排查

### 数据显示为空

✅ 已修复 - 后端数组展平问题

### 请求超时

✅ 已修复 - 增加超时控制 + 线程池优化

### MMDB查询错误

✅ 已修复 - 改用 `maxminddb` 库

### 日志文件过多

✅ 已修复 - 统一日志管理系统

详细排查步骤请查看: [docs/完整文档.md](docs/完整文档.md#故障排查)

## 📈 更新日志

### v1.3.0 (2026-01-26)
- ✅ 统一日志系统 (自动轮转+压缩)
- ✅ 归档管理策略 (30天+90天)
- ✅ 启动自动清理

### v1.2.0 (2026-01-26)
- ✅ 集成 MaxMind GeoLite2
- ✅ 多数据库查询优先级
- ✅ 本地命中率提升至95%+

### v1.1.0 (2026-01-26)
- ✅ 集成 IPinfo MMDB
- ✅ 城市中文映射 (200+)
- ✅ 性能优化 (API调用减少90%)

### v1.0.0 (2024-11-25)
- ✅ 初始版本发布

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

- 项目维护: Tangjin
- 技术支持: 查看 [完整文档](docs/完整文档.md)

---

**⭐ 如果这个项目对您有帮助，请给个星标！**
