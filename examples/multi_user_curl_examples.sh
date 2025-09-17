#!/bin/bash
# -*- coding: utf-8 -*-
# 多用户模式 cURL 调用示例

echo "🚀 多用户 Google Drive API - cURL 调用示例"
echo "=================================================="

# 配置变量 - 这些是应用开发者的凭据，不是用户的！
# ⚠️ 重要说明：用户无需获取任何凭据，只需要有 Google 账户即可
BASE_URL="http://localhost:8080"
CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"    # 开发者在 Google Console 创建
CLIENT_SECRET="GOCSPX-YOUR_CLIENT_SECRET"                # 与 CLIENT_ID 配套
REDIRECT_URI="http://localhost:8080/callback"

echo ""
echo "⚙️  应用配置信息 (开发者凭据):"
echo "   服务地址: $BASE_URL"
echo "   应用客户端ID: $CLIENT_ID"
echo "   重定向URI: $REDIRECT_URI"

if [ "$CLIENT_ID" == "YOUR_CLIENT_ID.apps.googleusercontent.com" ]; then
    echo ""
    echo "❌ 请先设置应用的 OAuth 凭据（开发者凭据）"
    echo "   在脚本开头修改 CLIENT_ID 和 CLIENT_SECRET 变量"
    echo ""
    echo "🔑 这些凭据的作用："
    echo "   • CLIENT_ID 和 CLIENT_SECRET 是应用开发者的凭据"
    echo "   • 用于标识您的应用，不是用户的凭据"
    echo "   • 用户只需要有 Google 账户，无需任何技术配置"
    echo ""
    echo "👨‍💻 开发者需要："
    echo "   1. 在 Google Cloud Console 创建项目"
    echo "   2. 启用 Google Drive API"
    echo "   3. 创建 OAuth 2.0 凭据"
    echo "   4. 将凭据填入此脚本"
    echo ""
    echo "👤 用户需要："
    echo "   1. 有 Google 账户"
    echo "   2. 点击授权链接并登录"
    echo "   3. 授权应用访问其 Google Drive"
    exit 1
fi

echo ""
echo "📋 多用户模式 API 调用示例"
echo "================================"

echo ""
echo "1️⃣ 获取用户授权 URL"
echo "-------------------"
echo "curl -X GET \"$BASE_URL/api/v1/multi-user/auth\" \\"
echo "  -G \\"
echo "  -d \"client_id=$CLIENT_ID\" \\"
echo "  -d \"client_secret=$CLIENT_SECRET\" \\"
echo "  -d \"redirect_uri=$REDIRECT_URI\""

echo ""
echo "💡 执行上述命令后，会返回授权 URL，用户需要访问该 URL 完成授权"

echo ""
echo "2️⃣ 处理授权回调（用户授权后）"
echo "-------------------------"
echo "curl -X POST \"$BASE_URL/api/v1/multi-user/auth/callback\" \\"
echo "  -F \"code=AUTHORIZATION_CODE_FROM_GOOGLE\" \\"
echo "  -F \"client_id=$CLIENT_ID\" \\"
echo "  -F \"client_secret=$CLIENT_SECRET\" \\"
echo "  -F \"redirect_uri=$REDIRECT_URI\""

echo ""
echo "💡 用户授权后，Google 会返回授权码，使用该授权码换取访问令牌"

echo ""
echo "3️⃣ 用户上传文件到自己的 Google Drive"
echo "--------------------------------"
echo "# 首先创建一个测试文件"
echo "echo \"用户的测试文件内容\" > user_test_file.txt"
echo ""
echo "# 上传文件（需要用户的访问令牌）"
echo "curl -X POST \"$BASE_URL/api/v1/multi-user/upload\" \\"
echo "  -H \"X-User-Token: {\\\"access_token\\\":\\\"ya29.a0AfH6SMC...\\\",\\\"refresh_token\\\":\\\"1//04...\\\",\\\"client_id\\\":\\\"$CLIENT_ID\\\",\\\"client_secret\\\":\\\"$CLIENT_SECRET\\\"}\" \\"
echo "  -F \"file=@user_test_file.txt\""

echo ""
echo "4️⃣ 列出用户自己的文件"
echo "-------------------"
echo "curl -X GET \"$BASE_URL/api/v1/multi-user/list\" \\"
echo "  -H \"X-User-Token: {\\\"access_token\\\":\\\"ya29.a0AfH6SMC...\\\",\\\"refresh_token\\\":\\\"1//04...\\\",\\\"client_id\\\":\\\"$CLIENT_ID\\\",\\\"client_secret\\\":\\\"$CLIENT_SECRET\\\"}\""

echo ""
echo "5️⃣ 搜索用户文件"
echo "-------------"
echo "curl -X GET \"$BASE_URL/api/v1/multi-user/list?query=name%20contains%20'test'&page_size=20\" \\"
echo "  -H \"X-User-Token: {\\\"access_token\\\":\\\"ya29.a0AfH6SMC...\\\",\\\"refresh_token\\\":\\\"1//04...\\\",\\\"client_id\\\":\\\"$CLIENT_ID\\\",\\\"client_secret\\\":\\\"$CLIENT_SECRET\\\"}\""

echo ""
echo "6️⃣ 下载用户文件"
echo "-------------"
echo "curl -X GET \"$BASE_URL/api/v1/multi-user/download/FILE_ID\" \\"
echo "  -H \"X-User-Token: {\\\"access_token\\\":\\\"ya29.a0AfH6SMC...\\\",\\\"refresh_token\\\":\\\"1//04...\\\",\\\"client_id\\\":\\\"$CLIENT_ID\\\",\\\"client_secret\\\":\\\"$CLIENT_SECRET\\\"}\" \\"
echo "  -o \"downloaded_user_file.txt\""

echo ""
echo "7️⃣ 获取用户信息"
echo "-------------"
echo "curl -X GET \"$BASE_URL/api/v1/multi-user/user-info\" \\"
echo "  -H \"X-User-Token: {\\\"access_token\\\":\\\"ya29.a0AfH6SMC...\\\",\\\"refresh_token\\\":\\\"1//04...\\\",\\\"client_id\\\":\\\"$CLIENT_ID\\\",\\\"client_secret\\\":\\\"$CLIENT_SECRET\\\"}\""

echo ""
echo "📝 用户令牌格式说明"
echo "=================="
echo "X-User-Token 头部需要包含 JSON 格式的用户令牌:"
echo "{"
echo "  \"access_token\": \"用户的访问令牌\","
echo "  \"refresh_token\": \"用户的刷新令牌\","
echo "  \"client_id\": \"您的客户端ID\","
echo "  \"client_secret\": \"您的客户端密钥\""
echo "}"

echo ""
echo "🔄 完整的多用户工作流程"
echo "===================="
echo "1. 用户A访问授权URL，完成Google账户授权"
echo "2. 系统获取用户A的访问令牌"
echo "3. 用户A使用自己的令牌上传文件到自己的Google Drive"
echo "4. 用户B重复同样的流程，获得自己的令牌"
echo "5. 用户B上传文件到自己的Google Drive"
echo "6. 用户A和用户B的文件完全隔离，互不影响"

echo ""
echo "🎯 实际使用示例"
echo "=============="

# 创建实际可执行的示例函数
function demo_get_auth_url() {
    echo "🔐 获取授权URL示例:"
    curl -X GET "$BASE_URL/api/v1/multi-user/auth" \
      -G \
      -d "client_id=$CLIENT_ID" \
      -d "client_secret=$CLIENT_SECRET" \
      -d "redirect_uri=$REDIRECT_URI" \
      2>/dev/null | jq . || echo "请求失败或服务未启动"
}

function demo_upload_with_token() {
    local USER_TOKEN="$1"
    if [ -z "$USER_TOKEN" ]; then
        echo "❌ 请提供用户令牌"
        return 1
    fi
    
    echo "📤 用户上传文件示例:"
    echo "用户测试文件内容 - $(date)" > test_upload.txt
    
    curl -X POST "$BASE_URL/api/v1/multi-user/upload" \
      -H "X-User-Token: $USER_TOKEN" \
      -F "file=@test_upload.txt" \
      2>/dev/null | jq . || echo "请求失败"
    
    rm -f test_upload.txt
}

function demo_list_files_with_token() {
    local USER_TOKEN="$1"
    if [ -z "$USER_TOKEN" ]; then
        echo "❌ 请提供用户令牌"
        return 1
    fi
    
    echo "📋 用户文件列表示例:"
    curl -X GET "$BASE_URL/api/v1/multi-user/list" \
      -H "X-User-Token: $USER_TOKEN" \
      2>/dev/null | jq . || echo "请求失败"
}

echo ""
echo "💻 交互式示例函数已定义:"
echo "   demo_get_auth_url                    # 获取授权URL"
echo "   demo_upload_with_token \"令牌JSON\"    # 上传文件"
echo "   demo_list_files_with_token \"令牌JSON\" # 列出文件"

echo ""
echo "📋 使用步骤:"
echo "1. 确保服务已启动: python main.py"
echo "2. 修改脚本中的CLIENT_ID和CLIENT_SECRET"
echo "3. 运行: source multi_user_curl_examples.sh"
echo "4. 调用: demo_get_auth_url"
echo "5. 让用户完成授权并获取令牌"
echo "6. 使用令牌调用其他函数"

echo ""
echo "🎉 多用户模式cURL示例准备完成!"
