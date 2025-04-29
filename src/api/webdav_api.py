from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.core.webdav_service import WebDAVService
import logging

router = APIRouter(prefix="/api/webdav", tags=["webdav"])

# 创建WebDAV服务实例
webdav_service = WebDAVService()

class WebDAVConfig(BaseModel):
    url: str
    username: str
    password: str

class BackupRequest(BaseModel):
    filename: Optional[str] = None

@router.post("/setup")
async def setup_webdav(config: WebDAVConfig):
    """设置WebDAV连接信息"""
    result = webdav_service.setup_webdav(config.url, config.username, config.password)
    if result:
        return {"success": True, "message": "WebDAV设置成功"}
    else:
        raise HTTPException(status_code=400, detail="WebDAV连接测试失败")

@router.get("/status")
async def get_status():
    """获取WebDAV状态信息"""
    return webdav_service.get_backup_status()

@router.post("/backup")
async def backup_data():
    """备份数据到WebDAV"""
    result = await webdav_service.backup_data()
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@router.get("/list")
async def list_backups():
    """获取备份列表"""
    try:
        backups = await webdav_service.list_backups()
        return backups
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"列出备份文件时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取备份列表失败: {str(e)}")

@router.post("/restore")
async def restore_backup(backup: BackupRequest):
    """从备份恢复数据"""
    if not backup.filename:
        raise HTTPException(status_code=400, detail="未指定备份文件名")
    
    result = await webdav_service.restore_backup(backup.filename)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@router.delete("/delete")
async def delete_backup(filename: str = Query(..., description="要删除的备份文件名")):
    """删除备份文件"""
    result = await webdav_service.delete_backup(filename)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@router.post("/test")
async def test_connection(config: Optional[WebDAVConfig] = None):
    """测试WebDAV连接"""
    if config:
        # 如果提供了新的配置，先尝试使用新配置测试
        result = webdav_service.test_connection_with_params(config.url, config.username, config.password)
    else:
        # 否则使用已保存的配置测试
        result = webdav_service.test_connection()
        
    if result:
        return {"success": True, "message": "连接测试成功"}
    else:
        raise HTTPException(status_code=400, detail="连接测试失败") 