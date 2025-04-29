import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件，如果不存在则创建默认配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 创建默认配置
                default_config = self.get_default_settings()
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"加载配置文件时出错: {str(e)}")
            # 出错时返回默认配置
            return self.get_default_settings()
            
    def get_default_settings(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "model_path": "models",
            "custom_nsfw_models": [],
            "theme": "light",
            "language": "zh_CN",
            "auto_check_update": True,
            "auto_update": False,
            "webdav_enabled": False,
            "webdav_url": "",
            "webdav_username": "",
            "webdav_password": "",
            "last_backup": None
        }
            
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置文件时出错: {str(e)}")
            return False
            
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config
        
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """更新配置并保存"""
        # 更新配置字典
        self.config.update(updates)
        # 保存到文件
        return self.save_config(self.config)
        
    def get_model_path(self) -> str:
        """获取模型路径"""
        return self.config.get('model_path', 'models')
        
    def update_model_path(self, path: str) -> bool:
        """更新模型路径"""
        self.config['model_path'] = path
        return self.save_config(self.config)
        
    def get_custom_nsfw_models(self) -> List[str]:
        """获取自定义NSFW模型列表"""
        return self.config.get('custom_nsfw_models', [])
        
    def update_custom_nsfw_models(self, models: List[str]) -> bool:
        """更新自定义NSFW模型列表"""
        self.config['custom_nsfw_models'] = models
        return self.save_config(self.config)
        
    def toggle_model_nsfw(self, model_name: str) -> bool:
        """切换模型的NSFW状态"""
        custom_nsfw_models = self.get_custom_nsfw_models()
        
        if model_name in custom_nsfw_models:
            custom_nsfw_models.remove(model_name)
        else:
            custom_nsfw_models.append(model_name)
            
        return self.update_custom_nsfw_models(custom_nsfw_models)
        
    def get_webdav_config(self) -> Dict[str, Any]:
        """获取WebDAV配置"""
        return {
            "enabled": self.config.get('webdav_enabled', False),
            "url": self.config.get('webdav_url', ''),
            "username": self.config.get('webdav_username', ''),
            "password": self.config.get('webdav_password', '')
        }
        
    def update_webdav_config(self, enabled: bool, url: str, username: str, password: str) -> bool:
        """更新WebDAV配置"""
        updates = {
            "webdav_enabled": enabled,
            "webdav_url": url,
            "webdav_username": username,
            "webdav_password": password
        }
        return self.update_config(updates)
        
    def get_last_backup_time(self) -> Optional[str]:
        """获取最后备份时间"""
        return self.config.get('last_backup')
        
    def update_last_backup_time(self, time_str: str) -> bool:
        """更新最后备份时间"""
        self.config['last_backup'] = time_str
        return self.save_config(self.config) 