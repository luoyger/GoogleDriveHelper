# -*- coding: utf-8 -*-
"""
多用户 Google Drive 路由
支持每个用户使用自己的 Google Drive 账户
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Header
from starlette.responses import JSONResponse, RedirectResponse

from service.multi_user_google_drive_service import multi_user_google_drive_service
from common.logger import logger

router = APIRouter(prefix="/multi-user", tags=["Multi-User Google Drive"])


@router.get("/auth")
async def get_auth_url(
    client_id: str = Query(..., description="OAuth 2.0 客户端 ID"),
    client_secret: str = Query(..., description="OAuth 2.0 客户端密钥"),
    redirect_uri: str = Query(..., description="重定向 URI")
):
    """
    获取用户授权 URL
    
    用户需要访问这个 URL 来授权应用访问他们的 Google Drive
    """
    try:
        auth_url = multi_user_google_drive_service.generate_auth_url(
            client_id, client_secret, redirect_uri
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "auth_url": auth_url,
                    "message": "请访问此 URL 进行授权"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取授权 URL 异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取授权 URL 失败: {str(e)}")


@router.post("/auth/callback")
async def auth_callback(
    code: str = Form(..., description="授权码"),
    client_id: str = Form(..., description="OAuth 2.0 客户端 ID"),
    client_secret: str = Form(..., description="OAuth 2.0 客户端密钥"),
    redirect_uri: str = Form(..., description="重定向 URI")
):
    """
    处理授权回调，换取访问令牌
    
    用户授权后，Google 会重定向到这个接口，携带授权码
    """
    try:
        token_data = multi_user_google_drive_service.exchange_code_for_token(
            code, client_id, client_secret, redirect_uri
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "token": token_data,
                    "message": "授权成功，请保存令牌用于后续 API 调用"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"授权回调处理异常: {e}")
        raise HTTPException(status_code=500, detail=f"授权处理失败: {str(e)}")


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    parent_folder_id: Optional[str] = Form(None, description="父文件夹ID（可选）"),
    user_token: str = Header(..., description="用户访问令牌", alias="X-User-Token")
):
    """
    上传文件到用户的 Google Drive
    
    - **file**: 要上传的文件
    - **parent_folder_id**: 可选，指定父文件夹ID
    - **X-User-Token**: 请求头中的用户令牌（JSON 格式）
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        logger.info(f"用户上传文件到自己的 Drive: {file.filename}")
        
        result = multi_user_google_drive_service.upload_file(file, user_token, parent_folder_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"多用户上传文件接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    user_token: str = Header(..., description="用户访问令牌", alias="X-User-Token")
):
    """
    从用户的 Google Drive 下载指定文件
    
    - **file_id**: Google Drive 文件ID
    - **X-User-Token**: 请求头中的用户令牌（JSON 格式）
    """
    try:
        logger.info(f"用户从自己的 Drive 下载文件: {file_id}")
        
        return multi_user_google_drive_service.download_file(file_id, user_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"多用户下载文件接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")


@router.get("/list")
async def list_files(
    query: Optional[str] = Query(None, description="搜索查询条件"),
    page_size: int = Query(100, ge=1, le=1000, description="每页文件数量，范围1-1000"),
    user_token: str = Header(..., description="用户访问令牌", alias="X-User-Token")
):
    """
    列出用户 Google Drive 中的文件
    
    - **query**: 可选，搜索查询条件
    - **page_size**: 每页返回的文件数量
    - **X-User-Token**: 请求头中的用户令牌（JSON 格式）
    """
    try:
        logger.info(f"用户获取自己的 Drive 文件列表，查询条件: {query}")
        
        result = multi_user_google_drive_service.list_files(user_token, query, page_size)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"多用户列出文件接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"列出文件失败: {str(e)}")


@router.get("/user-info")
async def get_user_info(
    user_token: str = Header(..., description="用户访问令牌", alias="X-User-Token")
):
    """
    获取当前用户的 Google Drive 信息
    
    - **X-User-Token**: 请求头中的用户令牌（JSON 格式）
    """
    try:
        # 创建用户专属服务来获取用户信息
        import json
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        token_data = json.loads(user_token)
        creds = Credentials(
            token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret')
        )
        
        service = build('drive', 'v3', credentials=creds)
        about = service.about().get(fields="user,storageQuota").execute()
        
        user_info = {
            'user': about.get('user', {}),
            'storage_quota': about.get('storageQuota', {}),
            'message': '用户信息获取成功'
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": user_info
            }
        )
        
    except Exception as e:
        logger.error(f"获取用户信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")
