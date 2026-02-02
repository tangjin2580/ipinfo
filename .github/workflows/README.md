# GitHub Workflows 使用说明

## 📋 概览

本项目包含三个现代化的 GitHub Actions 工作流：

| 工作流 | 文件 | 触发条件 | 用途 |
|--------|------|----------|------|
| **CI** | `ci.yml` | 推送到 main/index/develop 分支，PR | 代码质量检查和测试 |
| **Docker** | `docker.yml` | 推送到 main/index 分支，创建标签 | 构建并推送 Docker 镜像 |
| **Release** | `release.yml` | 创建版本标签 (v*.*.* 格式) | 创建 GitHub Release |

## 🔧 必需的 GitHub Secrets 配置

### Docker Hub 配置 (可选)

如果需要推送到 Docker Hub，请在 GitHub 仓库设置中添加以下 Secrets：

- `DOCKER_USERNAME` - Docker Hub 用户名
- `DOCKER_PASSWORD` - Docker Hub 密码或访问令牌

### 阿里云容器镜像服务配置 (可选)

如果需要推送到阿里云，请添加以下 Secrets：

- `ALIYUN_USERNAME` - 阿里云容器镜像服务用户名
- `ALIYUN_PASSWORD` - 阿里云容器镜像服务密码

> 💡 **提示**: 如果不配置这些 Secrets，Docker 镜像构建仍会正常进行，但不会推送到远程仓库。

## 📖 工作流详细说明

### 1️⃣ CI 工作流 (`ci.yml`)

**功能:**
- ✅ 在多个 Python 版本上测试 (3.8, 3.10, 3.12)
- ✅ 代码质量检查 (flake8)
- ✅ 项目结构验证
- ✅ 自动运行测试 (如果存在)
- ✅ 前端文件检查

**触发条件:**
- 推送到 `main`, `index`, `develop` 分支
- 创建 Pull Request
- 手动触发

**使用示例:**
```bash
# 每次推送代码时自动运行
git push origin index
```

### 2️⃣ Docker 工作流 (`docker.yml`)

**功能:**
- 🐳 构建多架构镜像 (amd64, arm64)
- 🚀 自动推送到 Docker Hub 和阿里云
- 🏷️ 智能标签管理
- 💾 构建缓存优化
- 📦 同时构建后端 (Flask) 和前端 (Nginx) 镜像

**触发条件:**
- 推送到 `main`, `index` 分支
- 创建版本标签
- 手动触发

**镜像标签规则:**
- `latest` - 主分支最新版本
- `v1.2.3` - 语义化版本号
- `index-abc123` - 分支名 + commit SHA

**使用示例:**
```bash
# 推送代码自动构建
git push origin main

# 创建标签自动构建并打版本标签
git tag v1.3.0
git push origin v1.3.0
```

### 3️⃣ Release 工作流 (`release.yml`)

**功能:**
- 📦 自动打包源码
- 📝 生成变更日志
- 🎉 创建 GitHub Release
- 📄 生成部署文档
- 💾 上传构建产物

**触发条件:**
- 创建 `v*.*.*` 格式的标签
- 手动触发 (可指定版本号)

**使用示例:**

```bash
# 方式 1: 创建标签自动发布
git tag v1.3.0
git push origin v1.3.0

# 方式 2: 在 GitHub Actions 页面手动触发
# 进入 Actions -> Release -> Run workflow
# 输入版本号: 1.3.0
```

**发布文件包含:**
- `ipinfo-source-v1.3.0.tar.gz` - 完整源代码包
- `RELEASE_NOTES.md` - 发布说明和变更日志

## 🚀 快速开始

### 步骤 1: 配置 Secrets

1. 进入仓库设置: `Settings` → `Secrets and variables` → `Actions`
2. 点击 `New repository secret`
3. 添加所需的 Secrets (见上方配置说明)

### 步骤 2: 推送代码测试 CI

```bash
# 推送到 index 分支触发 CI
git checkout index
git add .
git commit -m "test: trigger CI workflow"
git push origin index
```

### 步骤 3: 构建 Docker 镜像

```bash
# 推送到 main 分支触发 Docker 构建
git checkout main
git merge index
git push origin main
```

### 步骤 4: 创建 Release

```bash
# 创建版本标签
git tag v1.3.0
git push origin v1.3.0

# 自动触发 Release 和 Docker 构建
```

## 🆚 新旧工作流对比

| 特性 | 旧工作流 (deploy.yml) | 新工作流 |
|------|---------------------|---------|
| Actions 版本 | v3 (已弃用) | v4/v5 (最新) |
| 构建方式 | Nuitka + PyInstaller | Docker 镜像 |
| 多版本测试 | ❌ | ✅ 3.8, 3.10, 3.12 |
| 代码检查 | ❌ | ✅ flake8 |
| Docker 支持 | ❌ | ✅ 多架构 |
| 变更日志 | ❌ | ✅ 自动生成 |
| 工件上传 | v3 (报错) | v4 (最新) |

## 🐛 故障排查

### 问题 1: Docker 推送失败

**原因**: 未配置 Docker Hub 或阿里云 Secrets

**解决方案**:
```bash
# 1. 检查 Secrets 是否配置
# 2. 如果不需要推送，工作流会跳过推送步骤但不会报错
```

### 问题 2: CI 测试失败

**原因**: 代码质量问题或缺少依赖

**解决方案**:
```bash
# 本地运行 flake8 检查
flake8 server --count --select=E9,F63,F7,F82 --show-source --statistics

# 修复依赖问题
pip install -r requirements.txt
```

### 问题 3: Release 创建失败

**原因**: 版本号格式不正确或标签已存在

**解决方案**:
```bash
# 使用正确的语义化版本格式
git tag v1.3.0  # ✅ 正确
git tag 1.3.0   # ❌ 错误

# 删除错误的标签
git tag -d v1.3.0
git push origin :refs/tags/v1.3.0
```

## 📚 更多信息

- [GitHub Actions 文档](https://docs.github.com/actions)
- [Docker Buildx 文档](https://docs.docker.com/buildx/working-with-buildx/)
- [语义化版本规范](https://semver.org/lang/zh-CN/)

## 📞 支持

如有问题，请在 GitHub Issues 中提出。

---

**✨ 更新日期**: 2026-02-02  
**🔧 维护者**: Tangjin
