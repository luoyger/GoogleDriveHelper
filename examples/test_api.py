#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive API 测试脚本
演示如何使用 Google Drive API 接口进行文件上传和下载
"""

import requests
import os
import time
import json
from pathlib import Path

# API 基础 URL
BASE_URL = "http://localhost:8080/api/v1/google-drive"


def create_test_file():
    """创建测试文件"""
    test_content = f"""
这是一个测试文件
创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
内容: 用于测试 Google Drive API 上传功能
"""
    test_file_path = "test_file.txt"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ 创建测试文件: {test_file_path}")
    return test_file_path


def test_health_check():
    """测试健康检查接口"""
    print("\n🔍 测试健康检查接口...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 健康检查成功: {result['message']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False


def test_upload_file(file_path):
    """测试文件上传"""
    print(f"\n📤 测试文件上传: {file_path}")
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            
            response = requests.post(f"{BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                file_id = result['data']['file_id']
                print(f"✅ 文件上传成功!")
                print(f"   文件ID: {file_id}")
                print(f"   文件名: {result['data']['name']}")
                print(f"   文件大小: {result['data']['size']} bytes")
                print(f"   MIME类型: {result['data']['mime_type']}")
                return file_id
            else:
                print(f"❌ 文件上传失败: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ 文件上传异常: {e}")
        return None


def test_list_files():
    """测试文件列表"""
    print("\n📋 测试文件列表...")
    
    try:
        response = requests.get(f"{BASE_URL}/list", params={'page_size': 10})
        
        if response.status_code == 200:
            result = response.json()
            files = result['data']['files']
            print(f"✅ 获取文件列表成功，共 {result['data']['count']} 个文件")
            
            if files:
                print("   最近的文件:")
                for i, file in enumerate(files[:5], 1):
                    print(f"   {i}. {file['name']} (ID: {file['id']})")
                    
                # 返回第一个文件的ID用于测试下载
                return files[0]['id'] if files else None
            else:
                print("   没有找到任何文件")
                return None
        else:
            print(f"❌ 获取文件列表失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 获取文件列表异常: {e}")
        return None


def test_get_file_info(file_id):
    """测试获取文件信息"""
    print(f"\n📄 测试获取文件信息: {file_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/file-info/{file_id}")
        
        if response.status_code == 200:
            result = response.json()
            file_info = result['data']
            print(f"✅ 获取文件信息成功:")
            print(f"   文件名: {file_info.get('name')}")
            print(f"   文件大小: {file_info.get('size')} bytes")
            print(f"   MIME类型: {file_info.get('mimeType')}")
            print(f"   创建时间: {file_info.get('createdTime')}")
            print(f"   修改时间: {file_info.get('modifiedTime')}")
            return True
        else:
            print(f"❌ 获取文件信息失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 获取文件信息异常: {e}")
        return False


def test_download_file(file_id):
    """测试文件下载"""
    print(f"\n📥 测试文件下载: {file_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/download/{file_id}", stream=True)
        
        if response.status_code == 200:
            # 从响应头获取文件名
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = f"downloaded_file_{file_id}"
            
            # 保存到 downloads 目录
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            save_path = os.path.join(downloads_dir, filename)
            
            # 下载文件
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            file_size = os.path.getsize(save_path)
            print(f"✅ 文件下载成功!")
            print(f"   保存路径: {save_path}")
            print(f"   文件大小: {file_size} bytes")
            return save_path
        else:
            print(f"❌ 文件下载失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 文件下载异常: {e}")
        return None


def test_search_files():
    """测试文件搜索"""
    print("\n🔍 测试文件搜索...")
    
    search_queries = [
        "name contains 'test'",
        "mimeType contains 'text/'",
        "name != '.DS_Store'"
    ]
    
    for query in search_queries:
        try:
            print(f"\n   搜索条件: {query}")
            response = requests.get(f"{BASE_URL}/list", params={'query': query, 'page_size': 5})
            
            if response.status_code == 200:
                result = response.json()
                files = result['data']['files']
                print(f"   ✅ 找到 {result['data']['count']} 个文件")
                
                for file in files[:3]:
                    print(f"      - {file['name']}")
            else:
                print(f"   ❌ 搜索失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 搜索异常: {e}")


def test_download_all_files():
    """测试下载所有文件"""
    print("\n📦 测试下载所有文件 (ZIP)...")
    
    try:
        # 只下载文本文件以减少测试时间
        response = requests.get(
            f"{BASE_URL}/download-all", 
            params={'query': "mimeType contains 'text/'"}, 
            stream=True
        )
        
        if response.status_code == 200:
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            zip_path = os.path.join(downloads_dir, "all_text_files.zip")
            
            with open(zip_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            file_size = os.path.getsize(zip_path)
            print(f"✅ 所有文件下载成功!")
            print(f"   ZIP文件路径: {zip_path}")
            print(f"   ZIP文件大小: {file_size} bytes")
            return zip_path
        else:
            print(f"❌ 下载所有文件失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 下载所有文件异常: {e}")
        return None


def cleanup_test_files():
    """清理测试文件"""
    print("\n🧹 清理测试文件...")
    
    files_to_remove = [
        "test_file.txt",
        "downloads"
    ]
    
    for item in files_to_remove:
        try:
            if os.path.isfile(item):
                os.remove(item)
                print(f"   ✅ 删除文件: {item}")
            elif os.path.isdir(item):
                import shutil
                shutil.rmtree(item)
                print(f"   ✅ 删除目录: {item}")
        except Exception as e:
            print(f"   ⚠️ 清理失败 {item}: {e}")


def main():
    """主测试函数"""
    print("🚀 Google Drive API 测试脚本")
    print("=" * 50)
    
    # 1. 健康检查
    if not test_health_check():
        print("\n❌ 服务不可用，请确保:")
        print("1. 服务器正在运行 (python main.py)")
        print("2. Google Drive API 已正确配置")
        print("3. 认证令牌已生成 (python setup_google_drive.py)")
        return
    
    # 2. 创建测试文件
    test_file_path = create_test_file()
    
    try:
        # 3. 测试文件上传
        uploaded_file_id = test_upload_file(test_file_path)
        
        # 4. 测试文件列表
        first_file_id = test_list_files()
        
        # 使用上传的文件ID或列表中的第一个文件ID
        test_file_id = uploaded_file_id or first_file_id
        
        if test_file_id:
            # 5. 测试获取文件信息
            test_get_file_info(test_file_id)
            
            # 6. 测试文件下载
            test_download_file(test_file_id)
        
        # 7. 测试文件搜索
        test_search_files()
        
        # 8. 测试下载所有文件
        test_download_all_files()
        
        print("\n🎉 所有测试完成!")
        
    finally:
        # 9. 清理测试文件
        cleanup_test_files()


if __name__ == '__main__':
    main()
