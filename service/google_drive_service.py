# -*- coding: utf-8 -*-
import os
import io
import zipfile
from typing import Optional, List, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from fastapi import HTTPException, UploadFile
from starlette.responses import StreamingResponse

from common.config_loader import GLOBAL_CONFIG
from common.logger import logger


class GoogleDriveService:
    def __init__(self):
        self.service = None
        self.credentials = None
        self._initialize_service()

    def _initialize_service(self):
        """初始化 Google Drive API 服务"""
        try:
            config = GLOBAL_CONFIG.get('google_drive', {})
            auth_method = config.get('auth_method', 'service_account')
            scopes = config.get('scopes', ['https://www.googleapis.com/auth/drive'])

            if auth_method == 'service_account':
                self.credentials = self._initialize_service_account(config, scopes)
            else:
                self.credentials = self._initialize_oauth(config, scopes)

            self.service = build('drive', 'v3', credentials=self.credentials)
            logger.info(f"Google Drive API 服务初始化成功 (认证方式: {auth_method})")
            
        except Exception as e:
            logger.error(f"初始化 Google Drive API 服务失败: {e}")
            raise HTTPException(status_code=500, detail=f"初始化 Google Drive API 服务失败: {str(e)}")

    def _initialize_service_account(self, config, scopes):
        """使用服务账号初始化"""
        service_account_path = config.get('service_account_path', 'data/service_account.json')
        
        if not os.path.exists(service_account_path):
            raise HTTPException(
                status_code=500, 
                detail=f"服务账号文件不存在: {service_account_path}。请创建服务账号并下载密钥文件。"
            )
        
        try:
            credentials = ServiceAccountCredentials.from_service_account_file(
                service_account_path, scopes=scopes
            )
            logger.info("服务账号认证初始化成功")
            return credentials
            
        except Exception as e:
            logger.error(f"服务账号认证失败: {e}")
            raise HTTPException(status_code=500, detail=f"服务账号认证失败: {str(e)}")

    def _initialize_oauth(self, config, scopes):
        """使用 OAuth 2.0 初始化"""
        token_path = config.get('token_path', 'data/token.json')
        credentials_path = config.get('credentials_path', 'data/credentials.json')

        creds = None
        # 如果存在 token.json，加载凭据
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        
        # 如果没有有效的凭据，进行授权流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # 保存刷新后的凭据
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                    logger.info("OAuth 令牌刷新成功")
                except Exception as e:
                    logger.error(f"刷新令牌失败: {e}")
                    raise HTTPException(status_code=401, detail="令牌已过期，请重新授权")
            else:
                if not os.path.exists(credentials_path):
                    raise HTTPException(
                        status_code=500, 
                        detail=f"OAuth 凭据文件不存在: {credentials_path}。请先设置 Google Drive API 凭据。"
                    )
                
                # 对于服务器环境，不能使用交互式流程
                raise HTTPException(
                    status_code=401, 
                    detail="需要授权。请运行设置脚本生成访问令牌，或改用服务账号认证。"
                )

        logger.info("OAuth 2.0 认证初始化成功")
        return creds

    def upload_file(self, file: UploadFile, parent_folder_id: Optional[str] = None) -> Dict[str, Any]:
        """上传文件到 Google Drive"""
        try:
            # 创建临时文件
            temp_file_path = f"/tmp/{file.filename}"
            with open(temp_file_path, "wb") as temp_file:
                content = file.file.read()
                temp_file.write(content)
            
            # 准备文件元数据
            file_metadata = {
                'name': file.filename,
            }
            
            # 如果指定了父文件夹，添加到元数据中
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            else:
                # 检查是否有默认文件夹配置（解决服务账号存储配额问题）
                config = GLOBAL_CONFIG.get('google_drive', {})
                default_folder_id = config.get('default_folder_id')
                if default_folder_id:
                    file_metadata['parents'] = [default_folder_id]
                    logger.info(f"使用默认文件夹: {default_folder_id}")
                elif config.get('auth_method') == 'service_account':
                    # 服务账号认证时，如果没有指定文件夹，给出友好提示
                    logger.warning("服务账号认证需要指定父文件夹 ID，建议配置 default_folder_id 或在请求中指定 parent_folder_id")
                    raise HTTPException(
                        status_code=400,
                        detail="服务账号没有存储配额，请指定 parent_folder_id 参数上传到共享文件夹，或在配置文件中设置 default_folder_id"
                    )
            
            # 创建媒体上传对象
            media = MediaFileUpload(temp_file_path, mimetype=file.content_type)
            
            # 上传文件
            uploaded_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,mimeType,createdTime'
            ).execute()
            
            # 清理临时文件
            os.remove(temp_file_path)
            
            logger.info(f"文件上传成功: {uploaded_file.get('name')} (ID: {uploaded_file.get('id')})")
            
            return {
                'file_id': uploaded_file.get('id'),
                'name': uploaded_file.get('name'),
                'size': uploaded_file.get('size'),
                'mime_type': uploaded_file.get('mimeType'),
                'created_time': uploaded_file.get('createdTime'),
                'message': '文件上传成功'
            }
            
        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            # 清理可能存在的临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")

    def download_file(self, file_id: str) -> StreamingResponse:
        """从 Google Drive 下载文件"""
        try:
            # 获取文件信息
            file_info = self.service.files().get(fileId=file_id, fields='name,mimeType,size').execute()
            file_name = file_info.get('name')
            mime_type = file_info.get('mimeType')
            
            # 下载文件内容
            request = self.service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"下载进度: {int(status.progress() * 100)}%")
            
            # 重置文件指针到开始
            file_io.seek(0)
            
            logger.info(f"文件下载成功: {file_name} (ID: {file_id})")
            
            # 返回流式响应
            return StreamingResponse(
                io.BytesIO(file_io.read()),
                media_type=mime_type or 'application/octet-stream',
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Length": str(len(file_io.getvalue()))
                }
            )
            
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")

    def list_files(self, query: Optional[str] = None, page_size: int = 100) -> Dict[str, Any]:
        """列出 Google Drive 中的文件"""
        try:
            # 构建查询参数
            search_query = query if query else ""
            
            # 执行文件列表请求
            results = self.service.files().list(
                q=search_query,
                pageSize=page_size,
                fields="nextPageToken, files(id,name,size,mimeType,createdTime,modifiedTime,parents)"
            ).execute()
            
            files = results.get('files', [])
            
            logger.info(f"找到 {len(files)} 个文件")
            
            return {
                'files': files,
                'count': len(files),
                'next_page_token': results.get('nextPageToken'),
                'message': f'成功获取 {len(files)} 个文件'
            }
            
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            raise HTTPException(status_code=500, detail=f"列出文件失败: {str(e)}")

    def download_all_files(self, query: Optional[str] = None) -> StreamingResponse:
        """下载所有文件为 ZIP 压缩包"""
        try:
            # 获取文件列表
            files_result = self.list_files(query=query)
            files = files_result['files']
            
            if not files:
                raise HTTPException(status_code=404, detail="没有找到任何文件")
            
            # 创建内存中的 ZIP 文件
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_info in files:
                    file_id = file_info['id']
                    file_name = file_info['name']
                    
                    try:
                        # 下载单个文件
                        request = self.service.files().get_media(fileId=file_id)
                        file_io = io.BytesIO()
                        downloader = MediaIoBaseDownload(file_io, request)
                        
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                        
                        # 将文件添加到 ZIP
                        file_io.seek(0)
                        zip_file.writestr(file_name, file_io.read())
                        logger.info(f"已添加到 ZIP: {file_name}")
                        
                    except Exception as e:
                        logger.warning(f"跳过文件 {file_name}: {e}")
                        continue
            
            # 重置缓冲区指针
            zip_buffer.seek(0)
            
            logger.info(f"成功创建包含 {len(files)} 个文件的 ZIP 压缩包")
            
            # 返回 ZIP 文件流
            return StreamingResponse(
                io.BytesIO(zip_buffer.read()),
                media_type='application/zip',
                headers={
                    "Content-Disposition": "attachment; filename=google_drive_files.zip"
                }
            )
            
        except Exception as e:
            logger.error(f"下载所有文件失败: {e}")
            raise HTTPException(status_code=500, detail=f"下载所有文件失败: {str(e)}")

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            file_info = self.service.files().get(
                fileId=file_id,
                fields='id,name,size,mimeType,createdTime,modifiedTime,parents,webViewLink,webContentLink'
            ).execute()
            
            logger.info(f"获取文件信息成功: {file_info.get('name')}")
            
            return file_info
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")


# 全局服务实例
google_drive_service = GoogleDriveService()
