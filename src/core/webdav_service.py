import os
import requests
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import aiohttp
import asyncio
from datetime import datetime
from urllib.parse import urlparse, unquote

from src.core.config_manager import ConfigManager

class WebDAVService:
    def __init__(self, config_file="config.json"):
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_config()
        # 确保data目录存在
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # 日志初始化
        self.logger = logging.getLogger(__name__)
        # 设置日志级别
        self.logger.setLevel(logging.DEBUG)
        # 确保日志处理器已添加
        if not self.logger.handlers:
            # 添加控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            self.logger.addHandler(console_handler)
            
            # 添加文件处理器，记录所有级别的日志
            log_dir = Path("logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_dir / "webdav.log")
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
        
    def setup_webdav(self, url: str, username: str, password: str) -> bool:
        """设置WebDAV连接信息"""
        webdav_config = {
            'webdav_url': url,
            'webdav_username': username,
            'webdav_password': password,
            'webdav_enabled': True,
            'last_backup': None
        }
        
        # 更新配置
        self.config_manager.update_config(webdav_config)
        
        # 测试连接
        if self.test_connection():
            self.logger.info("WebDAV连接测试成功")
            return True
        else:
            # 设置为禁用
            self.config_manager.update_config({'webdav_enabled': False})
            self.logger.error("WebDAV连接测试失败")
            return False
            
    def test_connection(self) -> bool:
        """测试WebDAV连接"""
        url = self.config.get('webdav_url', '')
        username = self.config.get('webdav_username', '')
        password = self.config.get('webdav_password', '')
        
        return self.test_connection_with_params(url, username, password)
        
    def test_connection_with_params(self, url: str, username: str, password: str) -> bool:
        """使用指定参数测试WebDAV连接"""
        if not url or not username or not password:
            return False
            
        try:
            # 确保URL以/结尾
            if not url.endswith('/'):
                url += '/'
                
            # 发送OPTIONS请求测试连接
            response = requests.options(url, auth=(username, password), timeout=10)
            return response.status_code in [200, 207]
        except Exception as e:
            self.logger.error(f"WebDAV连接测试失败: {str(e)}")
            return False
            
    async def ensure_directory_exists(self, url: str, username: str, password: str) -> bool:
        """确保WebDAV上的目录存在，如果不存在则尝试创建"""
        try:
            # 测试目录是否存在
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    'PROPFIND',
                    url,
                    auth=aiohttp.BasicAuth(username, password),
                    headers={'Depth': '0'},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 207:  # 目录存在
                        return True
                    elif response.status == 404:  # 目录不存在
                        # 对于坚果云，无法通过WebDAV创建根目录，需要在网页版创建
                        if 'jianguoyun.com' in url:
                            self.logger.error("使用坚果云时，请确保目录已在网页版创建")
                            return False
                        
                        # 创建目录
                        async with session.request(
                            'MKCOL',
                            url,
                            auth=aiohttp.BasicAuth(username, password),
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as mkcol_response:
                            if mkcol_response.status in [201, 200, 204]:
                                self.logger.info(f"成功创建目录: {url}")
                                return True
                            else:
                                error_text = await mkcol_response.text()
                                self.logger.error(f"创建目录失败: {url}, 状态码: {mkcol_response.status}, 错误: {error_text}")
                                return False
                    else:
                        self.logger.error(f"检查目录时返回意外状态码: {response.status}")
                        return False
        except Exception as e:
            self.logger.error(f"检查/创建目录失败: {str(e)}")
            return False
            
    async def backup_data(self) -> Dict[str, Any]:
        """备份data文件夹到WebDAV服务器"""
        if not self.config.get('webdav_enabled', False):
            return {"success": False, "message": "WebDAV未启用"}
            
        url = self.config.get('webdav_url', '')
        username = self.config.get('webdav_username', '')
        password = self.config.get('webdav_password', '')
        
        if not url or not username or not password:
            return {"success": False, "message": "WebDAV配置不完整"}
            
        # 检查data目录是否存在且有内容
        if not self.data_dir.exists():
            return {"success": False, "message": "备份失败: data目录不存在"}
            
        # 确保URL以/结尾
        if not url.endswith('/'):
            url += '/'
            
        # 确保WebDAV目录存在
        dir_exists = await self.ensure_directory_exists(url, username, password)
        if not dir_exists:
            return {"success": False, "message": "备份失败: WebDAV目录不存在或无法创建。如果使用坚果云，请确保在网页版中已创建该目录。"}
            
        # 创建临时zip文件
        backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"sd_models_backup_{backup_time}.zip"
        temp_zip_path = Path(f"temp_{backup_filename}")
        # 完整的zip文件路径
        zip_path = temp_zip_path.with_suffix('.zip')
        
        try:
            # 压缩data文件夹
            shutil.make_archive(
                str(temp_zip_path.with_suffix('')),  # 去掉.zip后缀，因为make_archive会自动添加
                'zip',
                root_dir='.',
                base_dir='data'
            )
            
            if not zip_path.exists() or zip_path.stat().st_size == 0:
                return {"success": False, "message": "备份失败: 无法创建备份文件"}
            
            # 上传到WebDAV
            upload_url = f"{url}{backup_filename}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    with open(zip_path, 'rb') as f:
                        file_data = f.read()
                        
                    headers = {
                        'Content-Type': 'application/octet-stream'
                    }
                    
                    async with session.put(
                        upload_url, 
                        data=file_data,
                        auth=aiohttp.BasicAuth(username, password),
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=300)  # 5分钟超时
                    ) as response:
                        if response.status in [200, 201, 204]:
                            # 更新最后备份时间
                            self.config_manager.update_config({'last_backup': time.time()})
                            return {"success": True, "message": f"备份成功: {backup_filename}"}
                        else:
                            error_text = await response.text()
                            self.logger.error(f"WebDAV上传失败: 状态码 {response.status}, 错误: {error_text}")
                            return {"success": False, "message": f"备份失败，状态码: {response.status}, 错误: {error_text[:100]}"}
            except aiohttp.ClientError as e:
                self.logger.error(f"WebDAV客户端错误: {str(e)}")
                return {"success": False, "message": f"WebDAV连接错误: {str(e)}"}
            except asyncio.TimeoutError:
                self.logger.error("WebDAV上传超时")
                return {"success": False, "message": "备份上传超时，可能是网络问题或文件过大"}
        except Exception as e:
            self.logger.error(f"备份失败: {str(e)}")
            return {"success": False, "message": f"备份失败: {str(e)}"}
        finally:
            # 清理临时文件
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception as e:
                    self.logger.error(f"清理临时文件失败: {str(e)}")
                
    async def list_backups(self) -> List[Dict[str, Any]]:
        """列出WebDAV上的所有备份"""
        if not self.config.get('webdav_enabled', False):
            return []
            
        url = self.config.get('webdav_url', '')
        username = self.config.get('webdav_username', '')
        password = self.config.get('webdav_password', '')
        
        if not url or not username or not password:
            return []
            
        # 确保URL以/结尾
        if not url.endswith('/'):
            url += '/'
            
        try:
            # 发送PROPFIND请求获取目录列表
            headers = {
                'Depth': '1',
                'Content-Type': 'application/xml'
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        'PROPFIND',
                        url,
                        auth=aiohttp.BasicAuth(username, password),
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)  # 30秒超时
                    ) as response:
                        if response.status == 207:  # 多状态响应
                            # 解析XML响应
                            text = await response.text()
                            self.logger.debug(f"WebDAV响应: {text[:500]}...")  # 日志记录前500个字符
                            
                            # 保存原始XML响应到文件，方便调试分析
                            try:
                                log_dir = Path("logs")
                                log_dir.mkdir(parents=True, exist_ok=True)
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                xml_file = log_dir / f"webdav_response_{timestamp}.xml"
                                with open(xml_file, 'w', encoding='utf-8') as f:
                                    f.write(text)
                                self.logger.debug(f"已保存WebDAV响应到: {xml_file}")
                            except Exception as e:
                                self.logger.error(f"保存WebDAV响应失败: {str(e)}")
                            
                            # 导入XML解析库
                            import xml.etree.ElementTree as ET
                            from io import StringIO
                            
                            try:
                                # 解析XML
                                root = ET.fromstring(text)
                                
                                # 查找所有响应
                                backups = []
                                
                                # 查找所有href标签，它们包含文件路径
                                namespaces = {
                                    'd': 'DAV:',
                                    'nc': 'http://nextcloud.org/ns',
                                    'oc': 'http://owncloud.org/ns',
                                    's': 'http://ns.jianguoyun.com',  # 坚果云
                                    'a': 'http://apache.org/dav/props/',  # Apache
                                    'o': 'http://oauth.net/core/1.0/', # OAuth
                                    'w': 'http://wikka.jsnx.com/wakka.php?wakka=',  # Wikka
                                    'v': 'vrtx'  # Vortex
                                }
                                
                                # 先尝试使用命名空间查找
                                found_items = False
                                
                                for response_tag in root.findall('.//d:response', namespaces):
                                    href = response_tag.find('.//d:href', namespaces)
                                    if href is not None:
                                        path = href.text
                                        
                                        # 检查是否是备份文件
                                        if path and 'sd_models_backup_' in path and path.endswith('.zip'):
                                            found_items = True
                                            # 从路径中提取文件名
                                            filename = path.split('/')[-1]
                                            if not filename:  # 如果路径以/结尾
                                                continue
                                                
                                            # 从文件名中提取时间
                                            try:
                                                time_str = filename.replace('sd_models_backup_', '').replace('.zip', '')
                                                backup_time = datetime.strptime(time_str, "%Y%m%d_%H%M%S")
                                                backups.append({
                                                    "filename": filename,
                                                    "time": backup_time.strftime("%Y-%m-%d %H:%M:%S"),
                                                    "timestamp": backup_time.timestamp()
                                                })
                                                self.logger.info(f"找到备份文件: {filename}")
                                            except Exception as e:
                                                self.logger.error(f"解析备份时间失败: {filename}, 错误: {str(e)}")
                                
                                if not backups:
                                    # 如果XML解析失败，尝试使用简单的文本解析方法
                                    self.logger.warning("XML解析未找到备份文件，尝试使用文本解析")
                                    backups = self._parse_backups_from_text(text)
                                
                                # 按时间排序
                                backups.sort(key=lambda x: x["timestamp"], reverse=True)
                                self.logger.info(f"共找到 {len(backups)} 个备份文件")
                                
                                # 如果使用命名空间没有找到任何项目，尝试不使用命名空间搜索
                                if not found_items or not backups:
                                    self.logger.warning("使用命名空间未找到备份文件，尝试直接搜索所有元素")
                                    # 直接尝试搜索所有带href标签的元素
                                    all_hrefs = root.findall('.//*href') + root.findall('.//href')
                                    
                                    for href in all_hrefs:
                                        path = href.text
                                        if path and 'sd_models_backup_' in path and path.endswith('.zip'):
                                            # 从路径中提取文件名
                                            filename = path.split('/')[-1]
                                            if not filename:  # 如果路径以/结尾
                                                continue
                                                
                                            # 检查是否已经添加过这个文件
                                            if any(b["filename"] == filename for b in backups):
                                                continue
                                                
                                            # 从文件名中提取时间
                                            try:
                                                time_str = filename.replace('sd_models_backup_', '').replace('.zip', '')
                                                backup_time = datetime.strptime(time_str, "%Y%m%d_%H%M%S")
                                                backups.append({
                                                    "filename": filename,
                                                    "time": backup_time.strftime("%Y-%m-%d %H:%M:%S"),
                                                    "timestamp": backup_time.timestamp()
                                                })
                                                self.logger.info(f"通过直接搜索找到备份文件: {filename}")
                                            except Exception as e:
                                                self.logger.error(f"解析备份时间失败: {filename}, 错误: {str(e)}")
                                    
                                    # 如果仍然没有找到备份，尝试使用文本解析
                                    if not backups:
                                        self.logger.warning("所有XML解析方法均未找到备份文件，尝试使用文本解析")
                                        text_backups = self._parse_backups_from_text(text)
                                        
                                        # 添加使用文本解析找到的备份
                                        for backup in text_backups:
                                            if not any(b["filename"] == backup["filename"] for b in backups):
                                                backups.append(backup)
                                    
                                    # 重新排序
                                    backups.sort(key=lambda x: x["timestamp"], reverse=True)
                                
                                return backups
                            except ET.ParseError as e:
                                self.logger.error(f"XML解析错误: {str(e)}")
                                # 尝试使用简单的文本解析方法作为备选
                                backups = self._parse_backups_from_text(text)
                                backups.sort(key=lambda x: x["timestamp"], reverse=True)
                                self.logger.info(f"使用文本解析找到 {len(backups)} 个备份文件")
                                return backups
                                
                        elif response.status == 401:
                            self.logger.error("WebDAV认证失败")
                            return []
                        else:
                            error_text = await response.text()
                            self.logger.error(f"获取WebDAV目录列表失败: 状态码 {response.status}, 错误: {error_text[:200]}")
                            return []
            except aiohttp.ClientError as e:
                self.logger.error(f"WebDAV客户端错误: {str(e)}")
                return []
            except asyncio.TimeoutError:
                self.logger.error("WebDAV列表请求超时")
                return []
            
            return []
        except Exception as e:
            self.logger.error(f"获取备份列表失败: {str(e)}")
            return []
            
    def _parse_backups_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从WebDAV响应文本中解析备份文件信息（备选方法）"""
        backups = []
        for line in text.split('\n'):
            if 'sd_models_backup_' in line and '.zip' in line:
                # 尝试找到所有可能的备份文件名
                start = 0
                while True:
                    start = line.find('sd_models_backup_', start)
                    if start == -1:
                        break
                        
                    filename_end = line.find('.zip', start) + 4
                    if filename_end > 4:  # 确保找到了.zip后缀
                        filename = line[start:filename_end]
                        
                        # 检查文件名是否符合格式
                        if self._is_valid_backup_filename(filename):
                            # 从文件名中提取时间
                            try:
                                time_str = filename.replace('sd_models_backup_', '').replace('.zip', '')
                                backup_time = datetime.strptime(time_str, "%Y%m%d_%H%M%S")
                                backups.append({
                                    "filename": filename,
                                    "time": backup_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    "timestamp": backup_time.timestamp()
                                })
                                self.logger.info(f"通过文本解析找到备份文件: {filename}")
                            except Exception as e:
                                self.logger.error(f"解析备份时间失败: {filename}, 错误: {str(e)}")
                                
                        start = filename_end
                    else:
                        break
                        
        return backups
        
    def _is_valid_backup_filename(self, filename: str) -> bool:
        """检查文件名是否是有效的备份文件名"""
        if not (filename.startswith('sd_models_backup_') and filename.endswith('.zip')):
            return False
            
        # 提取时间部分并验证
        try:
            time_str = filename.replace('sd_models_backup_', '').replace('.zip', '')
            if len(time_str) != 15:  # YYYYMMDD_HHMMSS格式应该是15个字符
                return False
                
            # 尝试解析时间
            datetime.strptime(time_str, "%Y%m%d_%H%M%S")
            return True
        except ValueError:
            return False
            
    async def restore_backup(self, filename: str) -> Dict[str, Any]:
        """从WebDAV恢复备份"""
        if not self.config.get('webdav_enabled', False):
            return {"success": False, "message": "WebDAV未启用"}
            
        url = self.config.get('webdav_url', '')
        username = self.config.get('webdav_username', '')
        password = self.config.get('webdav_password', '')
        
        if not url or not username or not password:
            return {"success": False, "message": "WebDAV配置不完整"}
            
        # 确保URL以/结尾
        if not url.endswith('/'):
            url += '/'
            
        # 临时文件路径
        temp_zip_path = Path(f"temp_restore_{filename}")
        
        try:
            # 下载备份文件
            download_url = f"{url}{filename}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        download_url,
                        auth=aiohttp.BasicAuth(username, password),
                        timeout=aiohttp.ClientTimeout(total=300)  # 5分钟超时
                    ) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            # 保存到临时文件
                            with open(temp_zip_path, 'wb') as f:
                                f.write(content)
                            
                            if not temp_zip_path.exists() or temp_zip_path.stat().st_size == 0:
                                return {"success": False, "message": "下载的备份文件为空"}
                            
                            # 备份当前data文件夹
                            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                            backup_dir = Path(f"data_backup_{current_time}")
                            
                            if self.data_dir.exists():
                                shutil.copytree(self.data_dir, backup_dir)
                                
                            # 清空当前data文件夹
                            if self.data_dir.exists():
                                shutil.rmtree(self.data_dir)
                                
                            # 解压备份
                            shutil.unpack_archive(temp_zip_path, ".")
                            
                            return {
                                "success": True, 
                                "message": f"恢复成功，原数据已备份至 {backup_dir}。需要重启应用以加载恢复的数据。",
                                "require_restart": True
                            }
                        elif response.status == 404:
                            return {"success": False, "message": f"备份文件不存在: {filename}"}
                        elif response.status == 401:
                            return {"success": False, "message": "WebDAV认证失败"}
                        else:
                            error_text = await response.text()
                            self.logger.error(f"下载备份失败: 状态码 {response.status}, 错误: {error_text}")
                            return {"success": False, "message": f"下载备份失败，状态码: {response.status}"}
            except aiohttp.ClientError as e:
                self.logger.error(f"WebDAV客户端错误: {str(e)}")
                return {"success": False, "message": f"WebDAV连接错误: {str(e)}"}
            except asyncio.TimeoutError:
                self.logger.error("WebDAV下载超时")
                return {"success": False, "message": "备份下载超时，可能是网络问题或文件过大"}
                
        except Exception as e:
            self.logger.error(f"恢复备份失败: {str(e)}")
            return {"success": False, "message": f"恢复备份失败: {str(e)}"}
        finally:
            # 清理临时文件
            if os.path.exists(temp_zip_path):
                try:
                    os.remove(temp_zip_path)
                except Exception as e:
                    self.logger.error(f"清理临时文件失败: {str(e)}")
                
    async def delete_backup(self, filename: str) -> Dict[str, Any]:
        """删除WebDAV上的备份"""
        if not self.config.get('webdav_enabled', False):
            return {"success": False, "message": "WebDAV未启用"}
            
        url = self.config.get('webdav_url', '')
        username = self.config.get('webdav_username', '')
        password = self.config.get('webdav_password', '')
        
        if not url or not username or not password:
            return {"success": False, "message": "WebDAV配置不完整"}
            
        # 确保URL以/结尾
        if not url.endswith('/'):
            url += '/'
            
        try:
            # 删除文件
            delete_url = f"{url}{filename}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.delete(
                        delete_url,
                        auth=aiohttp.BasicAuth(username, password),
                        timeout=aiohttp.ClientTimeout(total=30)  # 30秒超时
                    ) as response:
                        if response.status in [200, 204, 404]:  # 成功或文件不存在
                            return {"success": True, "message": f"删除成功: {filename}"}
                        elif response.status == 401:
                            return {"success": False, "message": "WebDAV认证失败"}
                        else:
                            error_text = await response.text()
                            self.logger.error(f"删除备份失败: 状态码 {response.status}, 错误: {error_text}")
                            return {"success": False, "message": f"删除失败，状态码: {response.status}"}
            except aiohttp.ClientError as e:
                self.logger.error(f"WebDAV客户端错误: {str(e)}")
                return {"success": False, "message": f"WebDAV连接错误: {str(e)}"}
            except asyncio.TimeoutError:
                self.logger.error("WebDAV删除请求超时")
                return {"success": False, "message": "删除请求超时，请稍后重试"}
                
        except Exception as e:
            self.logger.error(f"删除备份失败: {str(e)}")
            return {"success": False, "message": f"删除备份失败: {str(e)}"}
            
    def get_backup_status(self) -> Dict[str, Any]:
        """获取备份状态"""
        last_backup = self.config.get('last_backup')
        webdav_enabled = self.config.get('webdav_enabled', False)
        
        if last_backup:
            last_backup_time = datetime.fromtimestamp(last_backup).strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_backup_time = None
            
        return {
            "enabled": webdav_enabled,
            "last_backup": last_backup_time,
            "last_backup_timestamp": last_backup,
            "url": self.config.get('webdav_url', ''),
            "username": self.config.get('webdav_username', '')
        } 