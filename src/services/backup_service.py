import asyncio
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.core.webdav_service import WebDAVService

class BackupService:
    def __init__(self, config_file="config.json"):
        self.webdav_service = WebDAVService(config_file)
        self.config = self.webdav_service.config
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
    async def start(self):
        """启动自动备份服务"""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._backup_loop())
        self.logger.info("自动备份服务已启动")
        
    async def stop(self):
        """停止自动备份服务"""
        if not self._running:
            return
            
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self.logger.info("自动备份服务已停止")
        
    async def _backup_loop(self):
        """备份循环"""
        while self._running:
            try:
                # 检查是否启用自动备份
                if not self.config.get('backup_enabled', True):
                    await asyncio.sleep(60)  # 如果未启用，每分钟检查一次
                    continue
                    
                # 检查是否启用WebDAV
                if not self.config.get('webdav_enabled', False):
                    await asyncio.sleep(60)  # 如果未启用，每分钟检查一次
                    continue
                    
                # 获取备份间隔（默认24小时）
                backup_interval = self.config.get('backup_interval', 86400)
                
                # 获取上次备份时间
                last_backup = self.config.get('last_backup')
                current_time = time.time()
                
                # 如果是首次备份或已经超过备份间隔
                if last_backup is None or (current_time - last_backup) > backup_interval:
                    self.logger.info("开始执行自动备份...")
                    result = await self.webdav_service.backup_data()
                    
                    if result["success"]:
                        self.logger.info(f"自动备份成功: {result['message']}")
                    else:
                        self.logger.error(f"自动备份失败: {result['message']}")
                        
                # 计算下次备份前的等待时间
                if last_backup:
                    next_backup_time = last_backup + backup_interval
                    wait_time = max(1, next_backup_time - current_time)
                else:
                    wait_time = backup_interval
                    
                # 等待到下次备份时间（但最多等待1小时，以便能够响应配置变化）
                await asyncio.sleep(min(wait_time, 3600))
                
            except Exception as e:
                self.logger.error(f"备份过程中出错: {str(e)}")
                await asyncio.sleep(300)  # 出错后等待5分钟再试
                
    async def clean_old_backups(self):
        """清理旧备份"""
        try:
            # 获取保留的备份数量
            backup_count = self.config.get('backup_count', 7)
            
            # 获取所有备份
            backups = await self.webdav_service.list_backups()
            
            # 如果备份数量超过限制，删除最旧的备份
            if len(backups) > backup_count:
                # 从最旧的开始删除
                backups_to_delete = backups[backup_count:]
                
                for backup in backups_to_delete:
                    filename = backup["filename"]
                    self.logger.info(f"删除旧备份: {filename}")
                    result = await self.webdav_service.delete_backup(filename)
                    
                    if not result["success"]:
                        self.logger.error(f"删除备份失败: {result['message']}")
                        
                return {"success": True, "message": f"已清理 {len(backups_to_delete)} 个旧备份"}
            else:
                return {"success": True, "message": "备份数量未超过限制，无需清理"}
                
        except Exception as e:
            self.logger.error(f"清理旧备份时出错: {str(e)}")
            return {"success": False, "message": f"清理失败: {str(e)}"} 