# -*- coding: utf-8 -*-
"""
多用户 Google Drive 服务
支持每个用户使用自己的 Google Drive 账户
"""

import os
import io
import zipfile
from typing import Optional, List, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from fastapi import HTTPException, UploadFile
from starlette.responses import StreamingResponse

from common.config_loader import GLOBAL_CONFIG
from common.logger import logger


class MultiUserGoogleDriveService:
    """多用户 Google Drive 服务"""
    
    def __init__(self):
        self.config = GLOBAL_CONFIG.get('google_drive', {})
        self.scopes = self.config.get('scopes', ['https://www.googleapis.com/auth/drive'])
    
    def _create_service_from_token(self, user_token: str):
        """根据用户令牌创建 Google Drive 服务"""
        try:
            # 解析用户令牌（这里假设是 JSON 格式的凭据）
            import json
            token_data = json.loads(user_token)
            
            # 创建凭据对象
            creds = Credentials(
                token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=self.scopes
            )
            
            # 检查并刷新令牌
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            # 创建服务
            service = build('drive', 'v3', credentials=creds)
            return service, creds
            
        except Exception as e:
            logger.error(f"创建用户服务失败: {e}")
            raise HTTPException(status_code=401, detail=f"用户认证失败: {str(e)}")
    
    def upload_file(self, file: UploadFile, user_token: str, parent_folder_id: Optional[str] = None) -> Dict[str, Any]:
        """上传文件到用户的 Google Drive"""
        try:
            # 创建用户专属服务
            service, creds = self._create_service_from_token(user_token)
            
            # 创建临时文件
            temp_file_path = f"/tmp/{file.filename}"
            with open(temp_file_path, "wb") as temp_file:
                content = file.file.read()
                temp_file.write(content)
            
            # 准备文件元数据
            file_metadata = {'name': file.filename}
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            # 创建媒体上传对象
            media = MediaFileUpload(temp_file_path, mimetype=file.content_type)
            
            # 上传文件到用户的 Drive
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,mimeType,createdTime'
            ).execute()
            
            # 清理临时文件
            os.remove(temp_file_path)
            
            logger.info(f"文件上传到用户 Drive 成功: {uploaded_file.get('name')}")
            
            return {
                'file_id': uploaded_file.get('id'),
                'name': uploaded_file.get('name'),
                'size': uploaded_file.get('size'),
                'mime_type': uploaded_file.get('mimeType'),
                'created_time': uploaded_file.get('createdTime'),
                'message': '文件上传到您的 Google Drive 成功'
            }
            
        except Exception as e:
            logger.error(f"上传文件到用户 Drive 失败: {e}")
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")
    
    def download_file(self, file_id: str, user_token: str) -> StreamingResponse:
        """从用户的 Google Drive 下载文件"""
        try:
            # 创建用户专属服务
            service, creds = self._create_service_from_token(user_token)
            
            # 获取文件信息
            file_info = service.files().get(fileId=file_id, fields='name,mimeType,size').execute()
            file_name = file_info.get('name')
            mime_type = file_info.get('mimeType')
            
            # 下载文件内容
            request = service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_io.seek(0)
            
            logger.info(f"从用户 Drive 下载文件成功: {file_name}")
            
            return StreamingResponse(
                io.BytesIO(file_io.read()),
                media_type=mime_type or 'application/octet-stream',
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Length": str(len(file_io.getvalue()))
                }
            )
            
        except Exception as e:
            logger.error(f"从用户 Drive 下载文件失败: {e}")
            raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")
    
    def list_files(self, user_token: str, query: Optional[str] = None, page_size: int = 100) -> Dict[str, Any]:
        """列出用户 Google Drive 中的文件"""
        try:
            # 创建用户专属服务
            service, creds = self._create_service_from_token(user_token)
            
            # 执行文件列表请求
            results = service.files().list(
                q=query if query else "",
                pageSize=page_size,
                fields="nextPageToken, files(id,name,size,mimeType,createdTime,modifiedTime,parents)"
            ).execute()
            
            files = results.get('files', [])
            
            logger.info(f"获取用户 Drive 文件列表成功，共 {len(files)} 个文件")
            
            return {
                'files': files,
                'count': len(files),
                'next_page_token': results.get('nextPageToken'),
                'message': f'成功获取您的 Google Drive 中的 {len(files)} 个文件'
            }
            
        except Exception as e:
            logger.error(f"获取用户 Drive 文件列表失败: {e}")
            raise HTTPException(status_code=500, detail=f"列出文件失败: {str(e)}")
    
    def generate_auth_url(self, client_id: str, client_secret: str, redirect_uri: str) -> str:
        """生成用户授权 URL"""
        try:
            from google_auth_oauthlib.flow import Flow
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = redirect_uri
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"生成授权 URL 失败: {e}")
            raise HTTPException(status_code=500, detail=f"生成授权 URL 失败: {str(e)}")
    
    def exchange_code_for_token(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> Dict[str, Any]:
        """将授权码换取访问令牌"""
        try:
            from google_auth_oauthlib.flow import Flow
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = redirect_uri
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            return {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
        except Exception as e:
            logger.error(f"换取访问令牌失败: {e}")
            raise HTTPException(status_code=500, detail=f"换取访问令牌失败: {str(e)}")


# 全局多用户服务实例
multi_user_google_drive_service = MultiUserGoogleDriveService()
