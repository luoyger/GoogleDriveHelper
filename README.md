# 🚀 Google Drive Helper

基于 FastAPI 的 Google Drive 文件管理 API 服务，提供文件上传、下载、列表查询等完整功能。

## 📋 项目概述

Google Drive Helper 是一个轻量级的后端服务，通过 RESTful API 接口实现与 Google Drive 的交互。支持个人账户认证，可以作为后台服务长期稳定运行。

### ✨ 核心特性

- 🔐 **OAuth 2.0 认证** - 支持个人 Google 账户，一次授权长期使用
- 📤 **文件上传** - 支持任意格式文件上传到 Google Drive
- 📥 **文件下载** - 通过文件 ID 下载单个文件
- 📦 **批量下载** - 将多个文件打包为 ZIP 下载
- 📋 **文件列表** - 支持搜索和分页的文件列表查询
- 📄 **文件信息** - 获取文件详细元数据信息
- 🔍 **高级搜索** - 支持按文件名、类型、文件夹等条件搜索
- ⚡ **自动刷新** - 访问令牌自动刷新，无需人工干预
- 🏥 **健康检查** - 内置服务状态监控接口

## 🏗️ 项目架构

```
GoogleDriveHelper/
├── main.py                 # 应用入口
├── config/                 # 配置文件
│   ├── config.yaml        # 主配置文件
│   ├── dev.yaml           # 开发环境配置
│   └── prod.yaml          # 生产环境配置
├── router/                 # API 路由
│   ├── router.py          # 路由注册
│   └── google_drive_router.py # Google Drive API 路由
├── service/                # 业务逻辑层
│   └── google_drive_service.py # Google Drive 服务类
├── common/                 # 公共模块
│   ├── config_loader.py   # 配置加载器
│   ├── logger.py          # 日志模块
│   └── utils.py           # 工具函数
├── data/                   # 数据文件
│   ├── credentials.json   # OAuth 凭据文件
│   └── token.json         # 访问令牌文件
└── examples/               # 示例代码
    └── test_api.py         # API 测试脚本
```

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.8+：

```bash
python --version
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. Google Drive API 配置

#### 步骤 1：创建 Google Cloud 项目
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google Drive API：
   - 导航到 **APIs & Services** → **库**
   - 搜索 "Google Drive API" 并启用

#### 步骤 2：配置 OAuth 同意屏幕
1. 导航到 **APIs & Services** → **OAuth 同意屏幕**
2. 选择 "外部" 用户类型
3. 填写必要信息：
   - 应用名称：`Google Drive Helper`
   - 用户支持电子邮件：您的邮箱
4. 在 **测试用户** 部分添加您的邮箱地址

#### 步骤 3：创建 OAuth 2.0 凭据
1. 导航到 **APIs & Services** → **凭据**
2. 点击 **创建凭据** → **OAuth 2.0 客户端 ID**
3. 选择应用类型：**桌面应用程序**
4. 下载 JSON 凭据文件
5. 将文件重命名为 `credentials.json` 并放置在 `data/` 目录下

#### 步骤 4：生成访问令牌
运行设置脚本进行一次性授权：

```bash
python setup.py
```

脚本会：
- 检查凭据文件
- 启动浏览器进行 OAuth 授权
- 生成长期有效的访问令牌
- 测试 API 连接

### 4. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8080` 启动

### 5. 验证安装

访问健康检查接口：
```bash
curl http://localhost:8080/health
```

## 📡 API 接口文档

### 基础信息
- **服务地址**: `http://localhost:8080`
- **API 前缀**: `/api/v1/google-drive`
- **响应格式**: JSON

### 接口列表

#### 1. 上传文件
```http
POST /api/v1/google-drive/upload
Content-Type: multipart/form-data
```

**参数:**
- `file` (必需): 要上传的文件
- `parent_folder_id` (可选): 目标文件夹 ID

**示例:**
```bash
curl -X POST http://localhost:8080/api/v1/google-drive/upload \
  -F "file=@document.pdf" \
  -F "parent_folder_id=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
```

#### 2. 下载文件
```http
GET /api/v1/google-drive/download/{file_id}
```

**示例:**
```bash
curl -X GET http://localhost:8080/api/v1/google-drive/download/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms \
  -o downloaded_file.pdf
```

#### 3. 列出文件
```http
GET /api/v1/google-drive/list?query={search_query}&page_size={size}
```

**参数:**
- `query` (可选): 搜索条件
- `page_size` (可选): 每页数量 (默认: 100, 最大: 1000)

**搜索语法示例:**
- `name contains 'report'` - 文件名包含 "report"
- `mimeType = 'application/pdf'` - PDF 文件
- `parents in 'FOLDER_ID'` - 指定文件夹中的文件

**示例:**
```bash
curl "http://localhost:8080/api/v1/google-drive/list?query=name contains 'test'&page_size=50"
```

#### 4. 批量下载
```http
GET /api/v1/google-drive/download-all?query={search_query}
```

将匹配的文件打包为 ZIP 下载。

#### 5. 获取文件信息
```http
GET /api/v1/google-drive/file-info/{file_id}
```

返回文件的详细元数据信息。

#### 6. 健康检查
```http
GET /api/v1/google-drive/health
```

检查服务运行状态。

### 响应格式

**成功响应:**
```json
{
  "success": true,
  "data": {
    "file_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "name": "document.pdf",
    "size": "1024000",
    "mime_type": "application/pdf",
    "created_time": "2025-09-16T10:30:00.000Z",
    "message": "操作成功"
  }
}
```

**错误响应:**
```json
{
  "detail": "错误描述信息"
}
```

## ⚙️ 配置说明

### 配置文件: `config/config.yaml`

```yaml
# 服务端口
port: 8080

# 日志配置
logger:
  level: INFO
  output: log/output.log
  backupCount: 30

# Google Drive 配置
google_drive:
  auth_method: oauth              # 认证方式
  credentials_path: data/credentials.json  # OAuth 凭据文件
  token_path: data/token.json     # 访问令牌文件
  scopes:
    - https://www.googleapis.com/auth/drive
```

### 环境配置

项目支持多环境配置：
- `config.yaml` - 默认配置
- `dev.yaml` - 开发环境配置
- `prod.yaml` - 生产环境配置

## 🧪 测试

### 运行测试脚本

```bash
python examples/test_api.py
```

测试脚本包含：
- 健康检查测试
- 文件上传测试
- 文件下载测试
- 文件列表测试
- 搜索功能测试
- 批量下载测试

### Python 代码示例

```python
import requests

# 上传文件
with open('test.txt', 'rb') as f:
    files = {'file': ('test.txt', f)}
    response = requests.post('http://localhost:8080/api/v1/google-drive/upload', files=files)
    result = response.json()
    file_id = result['data']['file_id']

# 下载文件
response = requests.get(f'http://localhost:8080/api/v1/google-drive/download/{file_id}')
with open('downloaded.txt', 'wb') as f:
    f.write(response.content)

# 列出文件
response = requests.get('http://localhost:8080/api/v1/google-drive/list')
files = response.json()['data']['files']
```

## 🚀 部署

### Docker 部署

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]
```

```bash
# 构建镜像
docker build -t google-drive-helper .

# 运行容器
docker run -d -p 8080:8080 -v $(pwd)/data:/app/data google-drive-helper
```

### 系统服务部署

```bash
# 创建 systemd 服务文件
sudo tee /etc/systemd/system/google-drive-helper.service > /dev/null <<EOF
[Unit]
Description=Google Drive Helper API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl enable google-drive-helper
sudo systemctl start google-drive-helper
```

## 🔒 安全建议

1. **保护凭据文件**
   ```bash
   chmod 600 data/credentials.json
   chmod 600 data/token.json
   ```

2. **版本控制排除**
   ```gitignore
   data/credentials.json
   data/token.json
   config/prod.yaml
   ```

3. **网络安全**
   - 使用 HTTPS 反向代理
   - 配置防火墙规则
   - 定期更新依赖包

4. **访问控制**
   - 设置 API 访问限制
   - 实施请求频率限制
   - 监控异常访问

## 🔧 故障排除

### 常见问题

**Q: 提示 "access_denied" 错误？**
A: 确保在 Google Cloud Console 的 OAuth 同意屏幕中添加了您的邮箱作为测试用户。

**Q: 令牌过期怎么办？**
A: 服务会自动刷新访问令牌。如果刷新令牌也过期，重新运行 `python setup.py`。

**Q: 上传大文件失败？**
A: 检查网络连接和 Google Drive 存储空间。可以增加请求超时时间。

**Q: 服务无法启动？**
A: 检查端口占用情况，确保所有依赖已正确安装。

### 日志查看

```bash
# 查看服务日志
tail -f log/output.log

# 查看系统服务日志
sudo journalctl -u google-drive-helper -f
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 📞 支持

如果您遇到问题或有建议，请：
- 查看故障排除部分
- 提交 [Issue](https://github.com/your-repo/GoogleDriveHelper/issues)
- 查看项目文档和示例代码

---

**🎉 享受使用 Google Drive Helper！**
