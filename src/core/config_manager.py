import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            return self.get_default_settings()
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.get_default_settings()
            
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
            
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config
        
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """更新配置"""
        self.config.update(new_config)
        return self.save_config()
        
    def get_model_path(self) -> str:
        """获取模型路径"""
        return self.config.get('model_path', '')
        
    def update_model_path(self, path: str) -> bool:
        """更新模型路径"""
        self.config['model_path'] = path
        return self.save_config()
        
    def get_custom_nsfw_models(self) -> List[str]:
        """获取自定义NSFW模型列表"""
        return self.config.get('custom_nsfw_models', [])
        
    def update_custom_nsfw_models(self, models: List[str]) -> bool:
        """更新自定义NSFW模型列表"""
        self.config['custom_nsfw_models'] = models
        return self.save_config()
        
    def toggle_model_nsfw(self, model_name: str) -> bool:
        """切换模型的NSFW状态"""
        models = self.get_custom_nsfw_models()
        if model_name in models:
            models.remove(model_name)
        else:
            models.append(model_name)
        return self.update_custom_nsfw_models(models)
        
    @staticmethod
    def get_default_settings() -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'model_path': '',
            'custom_nsfw_models': [],
            'theme': 'light',
            'language': 'zh_CN',
            'auto_update': True,
            'check_interval': 3600,  # 1小时
            'max_history': 100,
            'backup_enabled': True,
            'backup_interval': 86400,  # 24小时
            'backup_count': 7
        } 