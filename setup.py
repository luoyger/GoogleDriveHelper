#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人后台服务 OAuth 设置脚本
一次授权，长期使用
"""

import os
import json
import sys
from pathlib import Path


def print_header():
    """打印标题"""
    print("🔧 个人后台服务 OAuth 设置")
    print("一次浏览器授权，长期后台运行")
    print("=" * 50)


def create_oauth_credentials():
    """创建 OAuth 凭据文件"""
    credentials_path = Path("data/credentials.json")
    
    if credentials_path.exists():
        print("✅ OAuth 凭据文件已存在")
        return True
    
    print("\n📋 需要创建 OAuth 凭据文件")
    print("请按照以下步骤操作：")
    
    print("\n1️⃣ 访问 Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("\n2️⃣ 创建项目并启用 API:")
    print("   • 创建新项目（如果没有）")
    print("   • APIs & Services → 库 → 搜索 'Google Drive API' → 启用")
    
    print("\n3️⃣ 配置 OAuth 同意屏幕:")
    print("   • APIs & Services → OAuth 同意屏幕")
    print("   • 选择 '外部' 用户类型")
    print("   • 填写应用名称等基本信息")
    print("   • 在测试用户中添加您的邮箱")
    
    print("\n4️⃣ 创建 OAuth 2.0 凭据:")
    print("   • APIs & Services → 凭据")
    print("   • 创建凭据 → OAuth 2.0 客户端 ID")
    print("   • 应用类型：桌面应用程序")
    print("   • 下载 JSON 文件")
    
    print("\n5️⃣ 保存凭据文件:")
    print(f"   • 将下载的文件重命名为：{credentials_path}")
    
    print("\n完成后请重新运行此脚本")
    return False


def generate_long_term_token():
    """生成长期访问令牌"""
    print("\n🔐 生成长期访问令牌...")
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials_path = "data/credentials.json"
        token_path = "data/token.json"
        
        creds = None
        
        # 检查现有令牌
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # 如果没有有效凭据，进行授权流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("🔄 刷新现有令牌...")
                    creds.refresh(Request())
                    print("✅ 令牌刷新成功")
                except Exception as e:
                    print(f"❌ 令牌刷新失败: {e}")
                    creds = None
            
            if not creds:
                print("🌐 启动浏览器进行授权...")
                print("请在浏览器中完成授权流程")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                
                # 使用本地服务器进行授权
                creds = flow.run_local_server(port=0)
                print("✅ 授权完成")
        
        # 保存凭据
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        # 测试 API 连接
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=5).execute()
        files = results.get('files', [])
        
        print("✅ 长期令牌生成成功")
        print(f"   令牌文件: {token_path}")
        print(f"   找到 {len(files)} 个文件")
        
        # 显示令牌信息
        token_data = json.loads(creds.to_json())
        if token_data.get('refresh_token'):
            print("✅ 包含刷新令牌 - 支持长期后台运行")
        else:
            print("⚠️ 没有刷新令牌 - 令牌过期后需要重新授权")
        
        return True
        
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install google-auth google-auth-oauthlib google-api-python-client")
        return False
    except Exception as e:
        print(f"❌ 生成令牌失败: {e}")
        return False


def test_backend_service():
    """测试后台服务"""
    print("\n🧪 测试后台服务...")
    
    try:
        # 停止现有服务
        os.system("pkill -f 'python main.py' 2>/dev/null")
        
        print("🚀 启动后台服务...")
        
        # 启动服务（后台运行）
        import subprocess
        import time
        
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务启动
        time.sleep(3)
        
        # 测试健康检查
        import requests
        response = requests.get('http://localhost:8080/health', timeout=5)
        
        if response.status_code == 200:
            print("✅ 后台服务启动成功")
            
            # 测试文件上传
            test_content = "测试后台服务上传功能"
            with open("test_backend.txt", "w", encoding="utf-8") as f:
                f.write(test_content)
            
            with open("test_backend.txt", "rb") as f:
                files = {"file": ("test_backend.txt", f)}
                response = requests.post(
                    'http://localhost:8080/api/v1/google-drive/upload',
                    files=files,
                    timeout=30
                )
            
            os.remove("test_backend.txt")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 文件上传测试成功")
                print(f"   文件ID: {result['data']['file_id']}")
                print("✅ 个人后台服务配置完成！")
                return True
            else:
                print(f"❌ 文件上传测试失败: {response.status_code}")
                print(f"   错误: {response.text}")
        else:
            print(f"❌ 服务健康检查失败: {response.status_code}")
        
        # 清理进程
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def show_backend_deployment():
    """显示后台部署说明"""
    print("\n🚀 后台服务部署说明:")
    print("-" * 30)
    
    print("\n1️⃣ 系统服务部署 (systemd):")
    print(f"""
sudo tee /etc/systemd/system/google-drive-helper.service > /dev/null <<EOF
[Unit]
Description=Google Drive Helper API
After=network.target

[Service]
Type=simple
User={os.getenv('USER')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH={os.getcwd()}

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable google-drive-helper
sudo systemctl start google-drive-helper
sudo systemctl status google-drive-helper
""")
    
    print("\n2️⃣ Docker 部署:")
    print("""
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]

# 构建和运行
docker build -t google-drive-helper .
docker run -d -p 8080:8080 -v $(pwd)/data:/app/data google-drive-helper
""")
    
    print("\n3️⃣ 进程管理 (PM2):")
    print("""
npm install -g pm2
pm2 start main.py --name google-drive-helper --interpreter python3
pm2 startup
pm2 save
""")
    
    print("\n4️⃣ 简单后台运行:")
    print("nohup python main.py > /dev/null 2>&1 &")
    
    print("\n💡 令牌管理提示:")
    print("• OAuth 令牌通常有效期很长（几个月到一年）")
    print("• 包含刷新令牌的情况下可以自动续期")
    print("• 建议定期检查令牌状态")
    print("• 可以设置监控脚本检查服务健康状态")


def main():
    """主函数"""
    print_header()
    
    # 检查并创建 OAuth 凭据
    if not create_oauth_credentials():
        return
    
    # 生成长期令牌
    if not generate_long_term_token():
        return
    
    # 测试后台服务
    if test_backend_service():
        show_backend_deployment()
        
        print("\n🎉 个人后台服务设置完成！")
        print("\n📋 后续使用:")
        print("• 服务会在后台持续运行")
        print("• 令牌会自动刷新（如果支持）")
        print("• 可以通过 API 上传/下载文件")
        print("• 无需再次浏览器授权")
    else:
        print("\n❌ 设置未完成，请检查错误信息")


if __name__ == '__main__':
    main()
