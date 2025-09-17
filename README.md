# 🚀 Google Drive Helper

基于 FastAPI 的 Google Drive 文件管理 API 服务，提供文件上传、下载、列表查询等完整功能。

## 📋 项目概述

Google Drive Helper 是一个轻量级的后端服务，通过 RESTful API 接口实现与 Google Drive 的交互。支持单一账户和多用户两种模式，可以作为后台服务长期稳定运行。

### 🔄 支持模式

| 特性 | 单一账户模式 | 多用户模式 |
|------|-------------|-----------|
| **文件存储** | 所有用户文件存储在管理员的 Drive | 每个用户文件存储在各自的 Drive |
| **权限管理** | 管理员控制所有文件 | 用户控制自己的文件 |
| **隐私性** | 较低（文件混合存储） | 高（文件完全隔离） |
| **配置复杂度** | 简单（一次配置） | 中等（每个用户需授权） |
| **适用场景** | 内部团队、文件共享 | 多租户应用、个人文件管理 |

### ✨ 核心特性

- 🔐 **OAuth 2.0 认证** - 支持个人 Google 账户，一次授权长期使用
- 👥 **多用户支持** - 每个用户使用自己的 Google Drive，文件完全隔离
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
│   ├── google_drive_router.py # Google Drive API 路由 (单一账户)
│   └── multi_user_router.py   # 多用户 API 路由
├── service/                # 业务逻辑层
│   ├── google_drive_service.py # Google Drive 服务类 (单一账户)
│   └── multi_user_google_drive_service.py # 多用户 Google Drive 服务
├── common/                 # 公共模块
│   ├── config_loader.py   # 配置加载器
│   ├── logger.py          # 日志模块
│   └── utils.py           # 工具函数
├── data/                   # 数据文件
│   ├── credentials.json   # OAuth 凭据文件
│   └── token.json         # 访问令牌文件
└── examples/               # 示例代码
    ├── test_api.py         # API 测试脚本 (单一账户)
    ├── test_multi_user_api.py # 多用户 API 测试脚本
    ├── multi_user_examples.py # Python 多用户客户端示例
    ├── multi_user_curl_examples.sh # cURL 多用户调用示例
    └── multi_user_javascript_example.html # 网页多用户示例
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

## 👥 多用户模式

### 概述
多用户模式允许每个用户使用自己的 Google Drive 账户，实现完全的文件隔离和隐私保护。

### 🔑 核心概念

#### 用户 ID vs Google 账户
- **用户 ID**: 应用内部的标识符，可以是任意名字（alice, bob, 张三）
- **Google 账户**: 实际的存储账户，由用户在 Google 授权页面选择
- **映射关系**: 用户 ID "alice" + Google 账户 yourname@gmail.com = 文件存储在 yourname@gmail.com 的 Drive

### 🔄 工作流程

```
用户A → 获取授权URL → Google授权页面 → 用户A的Google账户登录 → 令牌A → 用户A的Drive
用户B → 获取授权URL → Google授权页面 → 用户B的Google账户登录 → 令牌B → 用户B的Drive
用户C → 获取授权URL → Google授权页面 → 用户C的Google账户登录 → 令牌C → 用户C的Drive
```

### 🧪 多用户测试方法

#### 方法 1：使用不同浏览器
- Chrome: 用户 ID "alice" → 用 Google 账户 A 授权
- Firefox: 用户 ID "bob" → 用 Google 账户 B 授权
- Safari: 用户 ID "charlie" → 用 Google 账户 C 授权

#### 方法 2：使用隐身模式
- 普通窗口: 用户 ID "alice" → 用 Google 账户 A 授权
- 隐身窗口: 用户 ID "bob" → 用 Google 账户 B 授权

#### 方法 3：手动切换 Google 账户
1. 在 Google 授权页面点击"使用其他账户"
2. 登录不同的 Google 账户
3. 完成授权流程

### 📋 多用户 API 接口

#### 1. 获取用户授权 URL
```http
GET /api/v1/multi-user/auth?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri={REDIRECT_URI}
```

**示例:**
```bash
curl -X GET "http://localhost:8080/api/v1/multi-user/auth" \
  -G \
  -d "client_id=your-client-id.apps.googleusercontent.com" \
  -d "client_secret=GOCSPX-your-client-secret" \
  -d "redirect_uri=http://localhost:8080/callback"
```

#### 2. 处理授权回调
```http
POST /api/v1/multi-user/auth/callback
Content-Type: multipart/form-data
```

**参数:**
- `code`: Google 返回的授权码
- `client_id`: OAuth 客户端 ID
- `client_secret`: OAuth 客户端密钥
- `redirect_uri`: 重定向 URI

#### 3. 用户上传文件
```http
POST /api/v1/multi-user/upload
Content-Type: multipart/form-data
X-User-Token: {USER_TOKEN_JSON}
```

**示例:**
```bash
curl -X POST "http://localhost:8080/api/v1/multi-user/upload" \
  -H "X-User-Token: {\"access_token\":\"ya29.a0AfH6SMC...\",\"client_id\":\"your-client-id\"}" \
  -F "file=@document.pdf"
```

#### 4. 用户列出文件
```http
GET /api/v1/multi-user/list?page_size={SIZE}&query={QUERY}
X-User-Token: {USER_TOKEN_JSON}
```

#### 5. 用户下载文件
```http
GET /api/v1/multi-user/download/{file_id}
X-User-Token: {USER_TOKEN_JSON}
```

#### 6. 获取用户信息
```http
GET /api/v1/multi-user/user-info
X-User-Token: {USER_TOKEN_JSON}
```

### 📱 多用户示例

#### Python 客户端示例
```python
# 运行完整的 Python 客户端示例
python examples/multi_user_examples.py
```

#### cURL 命令示例
```bash
# 运行 cURL 示例脚本
source examples/multi_user_curl_examples.sh
```

#### 网页界面示例
```bash
# 在浏览器中打开
examples/multi_user_javascript_example.html
```

#### API 测试脚本
```bash
# 运行多用户 API 测试
python examples/test_multi_user_api.py
```

## 📡 API 接口文档 (单一账户模式)

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

### 单一账户模式测试

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

### 多用户模式测试

```bash
# 运行多用户 API 测试
python examples/test_multi_user_api.py

# 运行 Python 客户端示例
python examples/multi_user_examples.py

# 运行 cURL 示例
source examples/multi_user_curl_examples.sh
```

多用户测试包含：
- 服务健康状态检查
- 多用户端点可用性测试
- 用户授权 URL 生成测试
- 用户令牌验证测试
- 错误处理测试
- 完整工作流程演示

### Python 代码示例

#### 单一账户模式
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

#### 多用户模式
```python
import requests
import json

# 1. 获取用户授权 URL
response = requests.get('http://localhost:8080/api/v1/multi-user/auth', params={
    'client_id': 'your-client-id.apps.googleusercontent.com',
    'client_secret': 'GOCSPX-your-client-secret',
    'redirect_uri': 'http://localhost:8080/callback'
})
auth_url = response.json()['data']['auth_url']
print(f"请用户访问: {auth_url}")

# 2. 用户授权后，换取访问令牌
# (用户授权后获得 authorization_code)
response = requests.post('http://localhost:8080/api/v1/multi-user/auth/callback', data={
    'code': 'authorization_code_from_google',
    'client_id': 'your-client-id.apps.googleusercontent.com',
    'client_secret': 'GOCSPX-your-client-secret',
    'redirect_uri': 'http://localhost:8080/callback'
})
user_token = response.json()['data']['token']

# 3. 用户上传文件到自己的 Drive
user_token_json = json.dumps(user_token)
with open('user_file.txt', 'rb') as f:
    files = {'file': ('user_file.txt', f)}
    response = requests.post('http://localhost:8080/api/v1/multi-user/upload', 
                           files=files,
                           headers={'X-User-Token': user_token_json})
    result = response.json()
    file_id = result['data']['file_id']

# 4. 用户列出自己的文件
response = requests.get('http://localhost:8080/api/v1/multi-user/list',
                       headers={'X-User-Token': user_token_json})
files = response.json()['data']['files']

# 5. 用户下载自己的文件
response = requests.get(f'http://localhost:8080/api/v1/multi-user/download/{file_id}',
                       headers={'X-User-Token': user_token_json})
with open('downloaded_user_file.txt', 'wb') as f:
    f.write(response.content)
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

#### 单一账户模式
**Q: 提示 "access_denied" 错误？**
A: 确保在 Google Cloud Console 的 OAuth 同意屏幕中添加了您的邮箱作为测试用户。

**Q: 令牌过期怎么办？**
A: 服务会自动刷新访问令牌。如果刷新令牌也过期，重新运行 `python setup.py`。

**Q: 上传大文件失败？**
A: 检查网络连接和 Google Drive 存储空间。可以增加请求超时时间。

**Q: 服务无法启动？**
A: 检查端口占用情况，确保所有依赖已正确安装。

#### 多用户模式
**Q: 为什么填写不同的用户 ID，还是跳转到我的 Google 账户？**
A: 用户 ID 只是应用内部的标识符，实际的 Google 账户由浏览器登录状态决定。要测试不同用户，需要：
- 使用不同浏览器（Chrome、Firefox、Safari）
- 使用隐身模式
- 在 Google 授权页面手动切换账户

**Q: 如何测试真正的多用户功能？**
A: 参考 README 中的"多用户测试方法"部分，使用不同浏览器或隐身模式，让不同的 Google 账户完成授权。

**Q: 前端出现 "Failed to execute 'fetch'" 错误？**
A: 检查用户令牌格式是否正确，确保是有效的 JSON 字符串。可以使用浏览器开发者工具查看详细错误信息。

**Q: 用户令牌格式是什么？**
A: 用户令牌是 JSON 格式的字符串，包含 access_token、refresh_token、client_id、client_secret 等字段。

**Q: 多用户模式下文件是否隔离？**
A: 是的，每个用户的文件存储在各自的 Google Drive 中，完全隔离。用户 A 无法访问用户 B 的文件。

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
