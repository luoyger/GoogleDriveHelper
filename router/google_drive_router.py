# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from starlette.responses import JSONResponse

from service.google_drive_service import google_drive_service
from common.logger import logger

router = APIRouter(prefix="/google-drive", tags=["Google Drive"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    parent_folder_id: Optional[str] = Form(None, description="父文件夹ID（可选）")
):
    """
    上传文件到 Google Drive
    
    - **file**: 要上传的文件
    - **parent_folder_id**: 可选，指定父文件夹ID
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        logger.info(f"开始上传文件: {file.filename}")
        
        result = google_drive_service.upload_file(file, parent_folder_id)
        
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
        logger.error(f"上传文件接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    从 Google Drive 下载指定文件
    
    - **file_id**: Google Drive 文件ID
    """
    try:
        logger.info(f"开始下载文件: {file_id}")
        
        return google_drive_service.download_file(file_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")


@router.get("/download-all")
async def download_all_files(
    query: Optional[str] = Query(None, description="搜索查询条件，用于过滤文件")
):
    """
    下载所有文件为ZIP压缩包
    
    - **query**: 可选，搜索查询条件来过滤文件
    """
    try:
        logger.info(f"开始下载所有文件，查询条件: {query}")
        
        return google_drive_service.download_all_files(query)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载所有文件接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"下载所有文件失败: {str(e)}")


@router.get("/list")
async def list_files(
    query: Optional[str] = Query(None, description="搜索查询条件"),
    page_size: int = Query(100, ge=1, le=1000, description="每页文件数量，范围1-1000")
):
    """
    列出 Google Drive 中的文件
    
    - **query**: 可选，搜索查询条件。例如：
      - `name contains 'test'` - 搜索文件名包含 'test' 的文件
      - `mimeType = 'image/jpeg'` - 搜索JPEG图片文件
      - `parents in 'FOLDER_ID'` - 搜索指定文件夹中的文件
    - **page_size**: 每页返回的文件数量
    """
    try:
        logger.info(f"列出文件，查询条件: {query}, 页面大小: {page_size}")
        
        result = google_drive_service.list_files(query, page_size)
        
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
        logger.error(f"列出文件接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"列出文件失败: {str(e)}")


@router.get("/file-info/{file_id}")
async def get_file_info(file_id: str):
    """
    获取指定文件的详细信息
    
    - **file_id**: Google Drive 文件ID
    """
    try:
        logger.info(f"获取文件信息: {file_id}")
        
        result = google_drive_service.get_file_info(file_id)
        
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
        logger.error(f"获取文件信息接口异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    检查 Google Drive 服务健康状态
    """
    try:
        # 尝试列出文件来检查服务是否正常
        google_drive_service.list_files(page_size=1)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Google Drive 服务运行正常"
            }
        )
        
    except Exception as e:
        logger.error(f"Google Drive 服务健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": f"Google Drive 服务不可用: {str(e)}"
            }
        )
