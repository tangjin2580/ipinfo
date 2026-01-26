# DNS解析对比工具

一个现代化的DNS解析对比工具，用于同时查询多个DNS服务器的解析结果并对比IP地理位置信息。

## ✨ 核心功能

- 🔍 **批量域名查询** - 支持同时输入多个域名进行批量解析
- 🌐 **多DNS对比** - 预设5个常用DNS服务器，支持自定义DNS
- 📊 **结果对比展示** - 表格形式展示解析结果，自动高亮IP差异
- 📜 **查询历史** - 自动保存查询历史，支持快速重新查询
- 📤 **数据导出** - 支持导出为CSV/JSON格式
- 🎨 **现代UI** - 深色主题 + 高端蓝紫渐变配色
- 📱 **响应式设计** - 完美适配桌面和移动设备

## 🚀 快速开始

### 直接使用

无需安装任何依赖，直接用浏览器打开 `index.html` 文件即可使用。

```bash
# 克隆或下载项目后
open index.html  # macOS
# 或直接双击 index.html 文件
```

### 使用本地服务器（可选）

```bash
# Python 3
python -m http.server 8000

# Node.js
npx serve

# 然后访问 http://localhost:8000
```

## 📖 使用说明

### 1. 输入域名

在左侧"域名输入"区域：
- 每行输入一个域名
- 或点击快捷按钮快速添加常用域名
- 支持的域名格式：`example.com`, `sub.example.com`

### 2. 选择DNS服务器

在右侧"DNS服务器选择"区域：
- 勾选预设的DNS服务器（默认选中Google和Cloudflare）
- 或输入自定义DNS服务器IP地址并点击"添加"

预设DNS服务器：
- `8.8.8.8` - Google DNS
- `1.1.1.1` - Cloudflare DNS
- `114.114.114.114` - 114 DNS（国内常用）
- `223.5.5.5` - 阿里DNS
- `180.76.76.76` - 百度DNS

### 3. 开始解析

点击"开始解析"按钮，系统将：
1. 验证域名格式
2. 向所有选中的DNS服务器发起查询
3. 展示解析结果并高亮IP差异
4. 自动保存到查询历史

### 4. 查看结果

解析结果表格包含以下信息：
- **域名** - 查询的域名
- **DNS服务器** - 使用的DNS服务器IP
- **解析IP** - 解析得到的IP地址（差异项会高亮显示）
- **国家** - IP所属国家
- **城市** - IP所属城市
- **运营商** - IP所属运营商/ISP
- **耗时** - DNS查询耗时（毫秒）

### 5. 导出数据

点击顶部的"导出CSV"或"导出JSON"按钮，可将当前结果导出为文件。

### 6. 查看历史

在"查询历史"区域：
- 显示最近10条查询记录
- 点击任意记录可快速重新查询
- 点击"清空历史"可清除所有本地历史记录

## 🔌 后端API集成

### API配置

修改 `index.html` 中的 `apiBaseUrl` 配置：

```javascript
data() {
    return {
        apiBaseUrl: 'http://localhost:8080',  // 修改为您的API地址
        // ...
    }
}
```

### API接口规范

#### 1. 批量查询

```http
POST /api/batch-query
Content-Type: application/json

{
  "domains": ["example.com", "test.com"],
  "dns_servers": ["8.8.8.8", "114.114.114.114"]
}
```

**响应示例：**
```json
[
  {
    "domain": "example.com",
    "ip": "93.184.216.34",
    "dns": "8.8.8.8",
    "country": "United States",
    "city": "Norwell",
    "isp": "EdgeCast Networks",
    "resolve_time": 45
  }
]
```

#### 2. 获取历史记录

```http
GET /api/history?limit=10
```

**响应示例：**
```json
[
  {
    "id": "uuid",
    "domain": "example.com",
    "ip": "93.184.216.34",
    "dns": "8.8.8.8",
    "country": "United States",
    "city": "Norwell",
    "isp": "EdgeCast Networks",
    "timestamp": "2026-01-26T14:08:57Z"
  }
]
```

#### 3. 清除缓存

```http
POST /api/clear-cache
```

**响应示例：**
```json
{
  "success": true,
  "message": "Cache cleared successfully"
}
```

## 🎯 演示模式

当后端API不可用时，工具会自动切换到**演示模式**，生成模拟数据用于功能展示。

演示模式特性：
- 自动生成合理的模拟解析结果
- 包含多个地理位置和运营商
- 支持所有前端功能（导出、历史记录等）

## 🛠 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Axios** - HTTP客户端
- **纯CSS** - 无UI框架依赖，全自定义样式
- **LocalStorage** - 本地历史记录存储

## 🎨 设计特色

- **深色科技主题** - 深邃太空蓝背景
- **高端蓝紫渐变** - 避免通用SaaS蓝，采用独特渐变配色
- **玻璃态效果** - 卡片采用Glassmorphism设计
- **流畅动画** - 微交互动画提升用户体验
- **响应式布局** - 移动端完美适配

## 📱 响应式断点

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: >= 1024px

## 🌐 浏览器兼容性

- Chrome/Edge: 最新版 - 2
- Firefox: 最新版 - 2
- Safari: 最新版 - 2
- 移动浏览器：iOS Safari 13+, Chrome Mobile

## ⚙️ 配置项

### 超时时间

默认API请求超时时间为30秒，可在代码中修改：

```javascript
const response = await axios.post(
    `${this.apiBaseUrl}/api/batch-query`,
    data,
    {
        timeout: 30000  // 修改超时时间（毫秒）
    }
);
```

### 历史记录数量

默认保存最新50条历史记录，可修改：

```javascript
// 只保留最新50条
this.history = this.history.slice(0, 50);  // 修改此数字
```

### 快捷域名

可在 `quickDomains` 数组中自定义快捷域名：

```javascript
quickDomains: [
    'google.com', 
    'baidu.com', 
    'github.com', 
    'youtube.com', 
    'taobao.com', 
    'qq.com'
]
```

## 🐛 故障排除

### API连接失败

1. 检查 `apiBaseUrl` 配置是否正确
2. 确认后端服务是否正常运行
3. 检查CORS配置（跨域问题）
4. 可暂时使用演示模式进行功能测试

### 历史记录丢失

历史记录存储在浏览器LocalStorage中，以下情况可能导致丢失：
- 清除浏览器数据
- 使用隐私/无痕模式
- 更换浏览器或设备

建议定期导出重要的查询结果。

### 域名格式错误

域名必须符合以下规则：
- 只包含字母、数字、连字符、点号
- 不能以连字符开头或结尾
- 至少包含一个点号（如 `example.com`）
- 示例：`example.com`, `sub.domain.com`

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 创建GitHub Issue
- 发送邮件至项目维护者

---

**作者**: Matrix Agent  
**版本**: 1.0.0  
**更新时间**: 2026-01-26
