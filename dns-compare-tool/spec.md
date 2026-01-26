# DNS解析对比工具 - 设计规格文档

## 项目概述

创建一个专业的DNS解析对比工具Web应用，用于同时查询多个DNS服务器的解析结果并对比IP地理位置信息。

## 设计系统

### 配色方案

**深色科技主题 - 高端蓝紫渐变**

- **背景色：** 
  - Primary: `#0a0e1a` (深邃太空蓝)
  - Secondary: `#151b2e` (深蓝灰)
  - Card: `#1a2234` (卡片背景)
  
- **强调色（高端蓝紫渐变）：**
  - Primary Gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` (紫罗兰到靛蓝)
  - Secondary Gradient: `linear-gradient(135deg, #5b86e5 0%, #36d1dc 100%)` (电光蓝到青色)
  - Accent Blue: `#6366f1` (现代靛蓝)
  - Accent Purple: `#8b5cf6` (皇家紫)
  
- **功能色：**
  - Success: `#10b981` (翠绿)
  - Warning: `#f59e0b` (琥珀)
  - Error: `#ef4444` (朱红)
  - Info: `#3b82f6` (天蓝)
  
- **文本色：**
  - Primary: `#f8fafc` (亮白)
  - Secondary: `#cbd5e1` (浅灰)
  - Muted: `#64748b` (中灰)

### 字体系统

- **主字体：** Inter, system-ui, -apple-system, sans-serif
- **等宽字体：** 'Fira Code', 'Consolas', monospace (用于IP地址显示)

**字阶：**
- H1: 2.5rem / 40px (页面标题)
- H2: 1.875rem / 30px (区块标题)
- H3: 1.5rem / 24px (卡片标题)
- Body: 1rem / 16px (正文)
- Small: 0.875rem / 14px (辅助信息)
- Tiny: 0.75rem / 12px (标签)

### 布局设计

**桌面布局（>=1024px）：**
```
+-----------------------------------------------+
|  [Logo] DNS解析对比工具        [清除缓存]     |
+-----------------------------------------------+
|                                               |
|  +-------------------+  +------------------+  |
|  | 域名输入区        |  | DNS服务器选择    |  |
|  | [textarea]        |  | □ 8.8.8.8       |  |
|  | [快捷按钮组]      |  | □ 1.1.1.1       |  |
|  +-------------------+  | [自定义输入]     |  |
|                         | [开始解析 按钮]  |  |
|                         +------------------+  |
|                                               |
|  +------------------------------------------+ |
|  |        解析结果表格                       | |
|  |  (对比差异高亮)                           | |
|  +------------------------------------------+ |
|                                               |
|  +------------------------------------------+ |
|  |        查询历史                           | |
|  +------------------------------------------+ |
+-----------------------------------------------+
```

**移动布局（<768px）：**
- 单列布局
- 折叠式区块
- 表格横向滚动

### 视觉元素

**玻璃态效果（Glassmorphism）：**
- 卡片使用半透明背景 + 模糊效果
- `backdrop-filter: blur(10px)`
- 边框使用渐变描边

**发光效果：**
- 按钮悬停时添加霓虹发光
- `box-shadow: 0 0 20px rgba(102, 126, 234, 0.5)`

**数据对比高亮：**
- 相同IP：正常显示
- 不同IP：使用渐变背景高亮
- 闪烁动画提示差异

### 动效设计

**加载动画：**
- DNS查询时显示脉冲圆环动画
- 渐变色旋转效果

**结果展示：**
- 数据行淡入 + 从下向上滑动
- stagger动画（依次出现）
- 持续时间：300ms，缓动函数：ease-out

**交互反馈：**
- 按钮按下：scale(0.95)
- 悬停：轻微上浮 + 发光
- 卡片悬停：边框渐变流动

## 技术栈

### 前端框架
- **Vue 3** (Composition API)
- **Vite** (构建工具)

### 核心库
- **Axios** (HTTP请求)
- **Vue Router** (可选，单页面可不用)

### UI组件
- **自定义组件** (避免重量级UI库)
- **Lucide Vue** (图标库)

### 工具库
- **Day.js** (时间处理)
- **Papa Parse** (CSV导出)

## API接口规格

### Base URL
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'
```

### 1. 批量查询
```
POST /api/batch-query
Content-Type: application/json

Request:
{
  "domains": ["example.com", "test.com"],
  "dns_servers": ["8.8.8.8", "114.114.114.114"]
}

Response:
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

### 2. 获取历史记录
```
GET /api/history?limit=10

Response:
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

### 3. 清除缓存
```
POST /api/clear-cache

Response:
{
  "success": true,
  "message": "Cache cleared successfully"
}
```

## 功能模块

### 1. 域名输入模块
- 多行文本框，支持批量输入
- 自动去除空行和前后空格
- 域名格式验证（正则：`^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$`）
- 快捷域名按钮：google.com, baidu.com, github.com, youtube.com, taobao.com

### 2. DNS服务器选择
预设服务器：
- 8.8.8.8 (Google DNS)
- 1.1.1.1 (Cloudflare)
- 114.114.114.114 (114 DNS)
- 223.5.5.5 (阿里DNS)
- 180.76.76.76 (百度DNS)

自定义输入：
- IP格式验证
- 支持添加多个自定义DNS

### 3. 解析结果展示
表格列：
- 域名
- DNS服务器
- 解析IP
- 国家
- 城市
- 运营商
- 解析时间(ms)

差异对比逻辑：
- 同一域名在不同DNS下的IP进行对比
- IP不一致时使用渐变背景标识
- 悬停显示详细差异信息

### 4. 历史记录
- 显示最近10条查询
- 显示时间戳（相对时间，如"5分钟前"）
- 点击历史记录重新加载配置
- 清空历史按钮

### 5. 数据导出
支持格式：
- CSV格式
- JSON格式

导出内容：
- 当前显示的所有解析结果
- 包含完整字段信息

## 性能优化

1. **请求优化**
   - 设置30秒超时
   - 失败重试机制（最多3次）
   - 并发请求控制

2. **渲染优化**
   - 虚拟滚动（结果超过100条时）
   - 防抖输入验证

3. **缓存策略**
   - LocalStorage存储历史记录
   - 与API历史记录合并展示

## 错误处理

- 网络错误：显示重试按钮
- API错误：显示错误信息toast
- 域名格式错误：输入框下方红色提示
- 超时错误：显示超时提示，建议减少查询数量

## 响应式断点

- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: >= 1024px

## 浏览器兼容性

- Chrome/Edge: 最新版 - 2
- Firefox: 最新版 - 2
- Safari: 最新版 - 2
- 移动浏览器：iOS Safari 13+, Chrome Mobile

## 部署配置

- 构建命令：`npm run build`
- 输出目录：`dist/`
- 环境变量：
  - `VITE_API_BASE_URL`: API基础URL

---

**设计原则：**
- 功能优先，美学第二
- 快速响应，流畅交互
- 信息清晰，对比直观
- 专业工具，技术美学
