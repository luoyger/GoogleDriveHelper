#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多用户模式 API 测试脚本
测试多用户 Google Drive API 的各个功能
"""

import requests
import json
import os
import time
from pathlib import Path


def print_header():
    """打印测试标题"""
    print("🧪 多用户 Google Drive API 测试")
    print("=" * 60)


def test_service_health():
    """测试服务健康状态"""
    print("\n🏥 测试服务健康状态...")
    
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务运行正常")
            return True
        else:
            print(f"⚠️ 服务状态异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务: {e}")
        print("\n请确保:")
        print("1. 服务已启动: python main.py")
        print("2. 服务地址正确: http://localhost:8080")
        return False


def test_get_auth_url():
    """测试获取授权 URL"""
    print("\n🔐 测试获取授权 URL...")
    
    # 注意: 这里需要替换为您的实际 OAuth 凭据
    test_client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
    test_client_secret = "GOCSPX-YOUR_CLIENT_SECRET"
    test_redirect_uri = "http://localhost:8080/callback"
    
    if test_client_id == "YOUR_CLIENT_ID.apps.googleusercontent.com":
        print("⚠️ 需要设置真实的 OAuth 凭据才能测试")
        print("请在代码中替换 test_client_id 和 test_client_secret")
        return False
    
    try:
        response = requests.get("http://localhost:8080/api/v1/multi-user/auth", params={
            'client_id': test_client_id,
            'client_secret': test_client_secret,
            'redirect_uri': test_redirect_uri
        })
        
        if response.status_code == 200:
            result = response.json()
            auth_url = result['data']['auth_url']
            print("✅ 授权 URL 获取成功")
            print(f"   URL: {auth_url[:100]}...")
            return True
        else:
            print(f"❌ 获取授权 URL 失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False


def test_multi_user_endpoints():
    """测试多用户端点可用性"""
    print("\n📡 测试多用户 API 端点...")
    
    endpoints = [
        ("GET", "/api/v1/multi-user/auth", "获取授权 URL"),
        ("POST", "/api/v1/multi-user/auth/callback", "处理授权回调"),
        ("POST", "/api/v1/multi-user/upload", "上传文件"),
        ("GET", "/api/v1/multi-user/list", "列出文件"),
        ("GET", "/api/v1/multi-user/download/test", "下载文件"),
        ("GET", "/api/v1/multi-user/user-info", "获取用户信息")
    ]
    
    available_endpoints = 0
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                # 对于 GET 请求，我们期望得到认证错误而不是 404
                response = requests.get(f"http://localhost:8080{endpoint}", timeout=5)
            else:
                # 对于 POST 请求，我们期望得到认证错误而不是 404
                response = requests.post(f"http://localhost:8080{endpoint}", timeout=5)
            
            if response.status_code == 404:
                print(f"❌ {description}: 端点不存在")
            elif response.status_code == 422:
                print(f"✅ {description}: 端点可用 (参数验证)")
                available_endpoints += 1
            elif response.status_code in [401, 403]:
                print(f"✅ {description}: 端点可用 (需要认证)")
                available_endpoints += 1
            else:
                print(f"✅ {description}: 端点可用 (状态码: {response.status_code})")
                available_endpoints += 1
                
        except Exception as e:
            print(f"❌ {description}: 测试失败 ({e})")
    
    print(f"\n📊 端点可用性: {available_endpoints}/{len(endpoints)}")
    return available_endpoints == len(endpoints)


def test_token_validation():
    """测试令牌验证"""
    print("\n🎫 测试令牌验证...")
    
    # 测试无效令牌
    invalid_token = '{"invalid": "token"}'
    
    try:
        response = requests.get("http://localhost:8080/api/v1/multi-user/list", headers={
            'X-User-Token': invalid_token
        })
        
        if response.status_code == 401 or response.status_code == 500:
            print("✅ 无效令牌正确被拒绝")
        else:
            print(f"⚠️ 无效令牌处理异常: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 令牌验证测试失败: {e}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    test_cases = [
        {
            "name": "缺少用户令牌",
            "method": "GET",
            "url": "http://localhost:8080/api/v1/multi-user/list",
            "expected_status": 422
        },
        {
            "name": "无效文件 ID",
            "method": "GET", 
            "url": "http://localhost:8080/api/v1/multi-user/download/invalid_id",
            "headers": {"X-User-Token": '{"test": "token"}'},
            "expected_status": [401, 500]
        }
    ]
    
    passed_tests = 0
    
    for test_case in test_cases:
        try:
            if test_case["method"] == "GET":
                response = requests.get(
                    test_case["url"],
                    headers=test_case.get("headers", {}),
                    timeout=5
                )
            else:
                response = requests.post(
                    test_case["url"],
                    headers=test_case.get("headers", {}),
                    timeout=5
                )
            
            expected = test_case["expected_status"]
            if isinstance(expected, list):
                if response.status_code in expected:
                    print(f"✅ {test_case['name']}: 错误处理正确")
                    passed_tests += 1
                else:
                    print(f"⚠️ {test_case['name']}: 状态码 {response.status_code} 不在预期范围 {expected}")
            else:
                if response.status_code == expected:
                    print(f"✅ {test_case['name']}: 错误处理正确")
                    passed_tests += 1
                else:
                    print(f"⚠️ {test_case['name']}: 期望 {expected}, 实际 {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {test_case['name']}: 测试失败 ({e})")
    
    print(f"\n📊 错误处理测试: {passed_tests}/{len(test_cases)} 通过")
    return passed_tests == len(test_cases)


def demo_workflow_explanation():
    """演示工作流程说明"""
    print("\n📋 多用户模式完整工作流程")
    print("=" * 50)
    
    workflow_steps = [
        {
            "step": "1. 配置 OAuth 凭据",
            "description": "在 Google Cloud Console 中创建 OAuth 2.0 凭据",
            "code": "client_id = 'your-client-id.apps.googleusercontent.com'\nclient_secret = 'GOCSPX-your-client-secret'"
        },
        {
            "step": "2. 获取用户授权 URL",
            "description": "为每个用户生成个人授权链接",
            "code": "GET /api/v1/multi-user/auth?client_id=...&client_secret=...&redirect_uri=..."
        },
        {
            "step": "3. 用户完成授权",
            "description": "用户点击链接，登录 Google 账户并授权",
            "code": "用户在浏览器中完成 Google OAuth 2.0 授权流程"
        },
        {
            "step": "4. 换取访问令牌",
            "description": "使用授权码获取用户的访问令牌",
            "code": "POST /api/v1/multi-user/auth/callback\ndata: {code, client_id, client_secret, redirect_uri}"
        },
        {
            "step": "5. 用户文件操作",
            "description": "用户使用自己的令牌操作自己的 Google Drive",
            "code": "POST /api/v1/multi-user/upload\nheaders: {'X-User-Token': user_token_json}"
        }
    ]
    
    for i, step in enumerate(workflow_steps, 1):
        print(f"\n{step['step']}")
        print(f"   {step['description']}")
        print(f"   示例: {step['code']}")
    
    print(f"\n🔒 关键特性:")
    print(f"   • 每个用户使用自己的 Google Drive 账户")
    print(f"   • 文件完全隔离，用户只能访问自己的文件")
    print(f"   • 使用用户自己的存储空间，不占用应用存储")
    print(f"   • 支持令牌自动刷新，长期稳定运行")


def create_example_usage_code():
    """创建示例使用代码"""
    print(f"\n💻 Python 客户端使用示例")
    print(f"=" * 40)
    
    example_code = '''
from examples.multi_user_examples import MultiUserGoogleDriveClient

# 1. 创建客户端
client = MultiUserGoogleDriveClient(
    base_url="http://localhost:8080",
    client_id="your-client-id.apps.googleusercontent.com",
    client_secret="GOCSPX-your-client-secret"
)

# 2. 为用户获取授权 URL
auth_url = client.get_auth_url("alice")
print(f"请用户访问: {auth_url}")

# 3. 用户授权后，换取令牌
token = client.exchange_code_for_token("alice", "authorization_code")

# 4. 用户上传文件到自己的 Drive
result = client.upload_file("alice", "document.pdf")

# 5. 用户列出自己的文件
files = client.list_files("alice")

# 6. 用户下载自己的文件
client.download_file("alice", file_id, "downloaded.pdf")
'''
    
    print(example_code)


def main():
    """主测试函数"""
    print_header()
    
    # 测试计数器
    total_tests = 0
    passed_tests = 0
    
    # 1. 服务健康检查
    total_tests += 1
    if test_service_health():
        passed_tests += 1
    
    # 2. 测试多用户端点
    total_tests += 1
    if test_multi_user_endpoints():
        passed_tests += 1
    
    # 3. 测试授权 URL 获取
    total_tests += 1
    if test_get_auth_url():
        passed_tests += 1
    
    # 4. 测试令牌验证
    total_tests += 1
    if test_token_validation():
        passed_tests += 1
    
    # 5. 测试错误处理
    total_tests += 1
    if test_error_handling():
        passed_tests += 1
    
    # 显示测试结果
    print(f"\n" + "=" * 60)
    print(f"📊 测试结果总结")
    print(f"=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"通过率: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 所有测试通过! 多用户模式 API 工作正常")
    else:
        print(f"\n⚠️ 部分测试失败，请检查服务配置")
    
    # 显示工作流程说明
    demo_workflow_explanation()
    
    # 显示示例代码
    create_example_usage_code()
    
    print(f"\n📋 下一步:")
    print(f"1. 设置 OAuth 2.0 凭据 (Google Cloud Console)")
    print(f"2. 运行 Python 示例: python examples/multi_user_examples.py")
    print(f"3. 运行 cURL 示例: source examples/multi_user_curl_examples.sh")
    print(f"4. 打开网页示例: examples/multi_user_javascript_example.html")


if __name__ == '__main__':
    main()
