#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多用户模式 Google Drive API 调用示例
演示如何让每个用户使用自己的 Google Drive 账户
"""

import requests
import json
import os
import time
from pathlib import Path


class MultiUserGoogleDriveClient:
    """多用户 Google Drive 客户端"""
    
    def __init__(self, base_url="http://localhost:8080", client_id=None, client_secret=None):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_tokens = {}  # 存储多个用户的令牌
    
    def get_auth_url(self, user_id, redirect_uri="http://localhost:8080/callback"):
        """获取用户授权 URL"""
        print(f"\n🔐 为用户 {user_id} 获取授权 URL...")
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/multi-user/auth", params={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': redirect_uri
            })
            
            if response.status_code == 200:
                result = response.json()
                auth_url = result['data']['auth_url']
                print(f"✅ 授权 URL 生成成功")
                print(f"   请让用户 {user_id} 访问: {auth_url}")
                return auth_url
            else:
                print(f"❌ 获取授权 URL 失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取授权 URL 异常: {e}")
            return None
    
    def exchange_code_for_token(self, user_id, auth_code, redirect_uri="http://localhost:8080/callback"):
        """将授权码换取用户令牌"""
        print(f"\n🔄 为用户 {user_id} 换取访问令牌...")
        
        try:
            response = requests.post(f"{self.base_url}/api/v1/multi-user/auth/callback", data={
                'code': auth_code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': redirect_uri
            })
            
            if response.status_code == 200:
                result = response.json()
                token_data = result['data']['token']
                
                # 存储用户令牌
                self.user_tokens[user_id] = json.dumps(token_data)
                
                print(f"✅ 用户 {user_id} 授权成功")
                print(f"   访问令牌: {token_data['access_token'][:20]}...")
                print(f"   刷新令牌: {'✅ 有' if token_data.get('refresh_token') else '❌ 无'}")
                
                return token_data
            else:
                print(f"❌ 换取令牌失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 换取令牌异常: {e}")
            return None
    
    def upload_file(self, user_id, file_path, parent_folder_id=None):
        """用户上传文件到自己的 Google Drive"""
        if user_id not in self.user_tokens:
            print(f"❌ 用户 {user_id} 未授权，请先获取令牌")
            return None
        
        print(f"\n📤 用户 {user_id} 上传文件: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {}
                if parent_folder_id:
                    data['parent_folder_id'] = parent_folder_id
                
                headers = {'X-User-Token': self.user_tokens[user_id]}
                
                response = requests.post(
                    f"{self.base_url}/api/v1/multi-user/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            if response.status_code == 200:
                result = response.json()
                file_info = result['data']
                print(f"✅ 用户 {user_id} 上传成功!")
                print(f"   文件ID: {file_info['file_id']}")
                print(f"   文件名: {file_info['name']}")
                print(f"   文件大小: {file_info['size']} bytes")
                return file_info
            else:
                print(f"❌ 用户 {user_id} 上传失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 用户 {user_id} 上传异常: {e}")
            return None
    
    def list_files(self, user_id, query=None, page_size=10):
        """列出用户自己 Google Drive 中的文件"""
        if user_id not in self.user_tokens:
            print(f"❌ 用户 {user_id} 未授权，请先获取令牌")
            return None
        
        print(f"\n📋 获取用户 {user_id} 的文件列表...")
        
        try:
            params = {'page_size': page_size}
            if query:
                params['query'] = query
            
            headers = {'X-User-Token': self.user_tokens[user_id]}
            
            response = requests.get(
                f"{self.base_url}/api/v1/multi-user/list",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                files = result['data']['files']
                print(f"✅ 用户 {user_id} 共有 {result['data']['count']} 个文件")
                
                if files:
                    print("   文件列表:")
                    for i, file in enumerate(files, 1):
                        print(f"   {i}. {file['name']} (ID: {file['id']})")
                
                return files
            else:
                print(f"❌ 获取用户 {user_id} 文件列表失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取用户 {user_id} 文件列表异常: {e}")
            return None
    
    def download_file(self, user_id, file_id, save_path=None):
        """用户从自己的 Google Drive 下载文件"""
        if user_id not in self.user_tokens:
            print(f"❌ 用户 {user_id} 未授权，请先获取令牌")
            return None
        
        print(f"\n📥 用户 {user_id} 下载文件: {file_id}")
        
        try:
            headers = {'X-User-Token': self.user_tokens[user_id]}
            
            response = requests.get(
                f"{self.base_url}/api/v1/multi-user/download/{file_id}",
                headers=headers,
                stream=True
            )
            
            if response.status_code == 200:
                # 从响应头获取文件名
                content_disposition = response.headers.get('Content-Disposition', '')
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                else:
                    filename = f"downloaded_{file_id}"
                
                if not save_path:
                    save_path = f"downloads/{user_id}_{filename}"
                
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                # 保存文件
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(save_path)
                print(f"✅ 用户 {user_id} 下载成功!")
                print(f"   保存路径: {save_path}")
                print(f"   文件大小: {file_size} bytes")
                return save_path
            else:
                print(f"❌ 用户 {user_id} 下载失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 用户 {user_id} 下载异常: {e}")
            return None
    
    def get_user_info(self, user_id):
        """获取用户的 Google Drive 信息"""
        if user_id not in self.user_tokens:
            print(f"❌ 用户 {user_id} 未授权，请先获取令牌")
            return None
        
        print(f"\n👤 获取用户 {user_id} 的 Drive 信息...")
        
        try:
            headers = {'X-User-Token': self.user_tokens[user_id]}
            
            response = requests.get(
                f"{self.base_url}/api/v1/multi-user/user-info",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                user_info = result['data']
                
                print(f"✅ 用户 {user_id} 信息获取成功:")
                if 'user' in user_info:
                    user_data = user_info['user']
                    print(f"   姓名: {user_data.get('displayName', 'Unknown')}")
                    print(f"   邮箱: {user_data.get('emailAddress', 'Unknown')}")
                
                if 'storage_quota' in user_info:
                    quota = user_info['storage_quota']
                    limit = int(quota.get('limit', 0))
                    usage = int(quota.get('usage', 0))
                    if limit > 0:
                        usage_percent = (usage / limit) * 100
                        print(f"   存储使用: {usage:,} / {limit:,} bytes ({usage_percent:.1f}%)")
                
                return user_info
            else:
                print(f"❌ 获取用户 {user_id} 信息失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取用户 {user_id} 信息异常: {e}")
            return None


def create_test_files():
    """创建测试文件"""
    print("📝 创建测试文件...")
    
    os.makedirs("test_files", exist_ok=True)
    
    test_files = []
    for i in range(1, 4):
        file_path = f"test_files/user_test_file_{i}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"这是测试文件 {i}\n")
            f.write(f"创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"用于测试多用户 Google Drive API\n")
        test_files.append(file_path)
        print(f"   ✅ 创建: {file_path}")
    
    return test_files


def cleanup_test_files():
    """清理测试文件"""
    print("\n🧹 清理测试文件...")
    
    import shutil
    for dir_name in ['test_files', 'downloads']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✅ 删除目录: {dir_name}")


def demo_multi_user_workflow():
    """演示多用户工作流程"""
    print("🚀 多用户 Google Drive API 演示")
    print("=" * 60)
    
    # ⚠️ 重要说明：这些是应用开发者的凭据，不是用户的！
    # 用户无需获取任何凭据，只需要有 Google 账户即可
    CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"      # 开发者在 Google Console 创建
    CLIENT_SECRET = "GOCSPX-YOUR_CLIENT_SECRET"                  # 与 CLIENT_ID 配套
    
    if CLIENT_ID == "YOUR_CLIENT_ID.apps.googleusercontent.com":
        print("❌ 请先设置应用的 OAuth 凭据（开发者凭据）")
        print("   这些是应用开发者在 Google Cloud Console 中获取的凭据")
        print("   用户无需获取任何凭据，只需要有 Google 账户即可")
        print("\n🔑 开发者需要做的：")
        print("   1. 在 Google Cloud Console 创建项目")
        print("   2. 启用 Google Drive API")
        print("   3. 创建 OAuth 2.0 凭据")
        print("   4. 将 CLIENT_ID 和 CLIENT_SECRET 替换到代码中")
        print("\n👤 用户需要做的：")
        print("   1. 有 Google 账户")
        print("   2. 点击授权链接")
        print("   3. 登录并授权应用")
        print("   4. 开始使用自己的 Google Drive")
        return
    
    # 创建客户端
    client = MultiUserGoogleDriveClient(
        base_url="http://localhost:8080",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    # 模拟多个用户
    users = ['alice', 'bob', 'charlie']
    
    print(f"\n👥 模拟 {len(users)} 个用户的工作流程")
    
    # 创建测试文件
    test_files = create_test_files()
    
    try:
        # 步骤 1: 为每个用户获取授权 URL
        print("\n" + "="*50)
        print("步骤 1: 用户授权流程")
        print("="*50)
        
        for user in users:
            auth_url = client.get_auth_url(user)
            if auth_url:
                print(f"\n📋 用户 {user} 需要完成以下操作:")
                print(f"   1. 访问授权 URL: {auth_url}")
                print(f"   2. 完成 Google 账户授权")
                print(f"   3. 获取授权码并调用 exchange_code_for_token()")
                
                # 在实际应用中，这里会等待用户完成授权并获取授权码
                # 为了演示，我们跳过这一步
                print(f"   ⚠️  演示模式: 跳过用户 {user} 的实际授权")
        
        print(f"\n💡 在实际应用中，每个用户需要:")
        print(f"   1. 点击授权链接")
        print(f"   2. 登录自己的 Google 账户")
        print(f"   3. 授权应用访问他们的 Google Drive")
        print(f"   4. 系统获取授权码并换取访问令牌")
        
        # 步骤 2: 模拟已授权用户的操作
        print(f"\n" + "="*50)
        print(f"步骤 2: 模拟已授权用户操作 (需要真实令牌)")
        print(f"="*50)
        
        print(f"\n📝 如果用户已完成授权，可以进行以下操作:")
        
        # 模拟用户操作示例代码
        example_operations = [
            "# 用户上传文件到自己的 Drive",
            "file_info = client.upload_file('alice', 'document.pdf')",
            "",
            "# 用户列出自己的文件",
            "files = client.list_files('alice', page_size=20)",
            "",
            "# 用户下载自己的文件", 
            "client.download_file('alice', file_id, 'downloaded_file.pdf')",
            "",
            "# 获取用户的 Drive 信息",
            "user_info = client.get_user_info('alice')"
        ]
        
        for line in example_operations:
            print(f"   {line}")
        
        # 步骤 3: 展示多用户隔离
        print(f"\n" + "="*50)
        print(f"步骤 3: 多用户文件隔离特性")
        print(f"="*50)
        
        print(f"\n🔒 文件隔离保证:")
        print(f"   • 用户 Alice 只能访问自己 Google Drive 中的文件")
        print(f"   • 用户 Bob 只能访问自己 Google Drive 中的文件")
        print(f"   • 用户 Charlie 只能访问自己 Google Drive 中的文件")
        print(f"   • 用户之间的文件完全隔离，无法互相访问")
        
        print(f"\n💾 存储空间:")
        print(f"   • 每个用户使用自己的 Google Drive 存储配额")
        print(f"   • 不会消耗应用管理员的存储空间")
        print(f"   • 用户可以管理自己的文件和权限")
        
    finally:
        # 清理测试文件
        cleanup_test_files()
    
    print(f"\n🎉 多用户模式演示完成!")
    print(f"\n📋 下一步:")
    print(f"   1. 在 Google Cloud Console 中设置 OAuth 2.0 凭据")
    print(f"   2. 更新代码中的 CLIENT_ID 和 CLIENT_SECRET")
    print(f"   3. 启动服务: python main.py")
    print(f"   4. 让用户完成授权流程")
    print(f"   5. 用户开始使用各自的 Google Drive!")


def demo_real_api_calls():
    """真实 API 调用演示（需要有效的用户令牌）"""
    print("\n🔧 真实 API 调用演示")
    print("=" * 40)
    
    # 这个函数展示如何在有真实用户令牌的情况下调用 API
    print("如果您已经有用户的访问令牌，可以这样使用:")
    
    example_token = {
        "access_token": "ya29.a0AfH6SMC...",
        "refresh_token": "1//04...",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "scopes": ["https://www.googleapis.com/auth/drive"]
    }
    
    print(f"\n📋 示例代码:")
    print(f"""
# 1. 直接设置用户令牌
client = MultiUserGoogleDriveClient()
client.user_tokens['user123'] = json.dumps({example_token})

# 2. 上传文件
result = client.upload_file('user123', 'my_document.pdf')

# 3. 列出文件
files = client.list_files('user123', query="name contains 'report'")

# 4. 下载文件
client.download_file('user123', 'file_id_here', 'downloaded.pdf')
""")


if __name__ == '__main__':
    # 运行演示
    demo_multi_user_workflow()
    demo_real_api_calls()
