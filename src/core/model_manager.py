import os
import json
import requests
from pathlib import Path
from typing import Dict, Any
import aiohttp
import aiofiles
from urllib.parse import urlparse
import time

from src.utils.hash_utils import HashUtils

class ModelManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.models_path = Path(self.config.get("models_path", "")) if self.config.get("models_path") else None
        self.api_base_url = "https://civitai.com/api/v1"
        self.models_info: Dict[str, Any] = {}
        self.images_path = Path("static/images")  # 添加图片保存路径
        self.images_path.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        self.hash_utils = HashUtils()
        
    def load_config(self) -> dict:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"models_path": "", "output_file": "models_info.json"}
    
    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def update_models_path(self, path: str):
        """更新模型路径"""
        self.models_path = Path(path)
        self.config["models_path"] = str(self.models_path)
        self.save_config()
    
    async def scan_models(self):
        """扫描指定目录下的所有.safetensors文件"""
        print(f"开始扫描目录: {self.models_path}")
        
        # 只扫描 checkpoints 和 loras 文件夹
        allowed_folders = ['checkpoints', 'loras']
        safetensors_files = []
        
        for folder in allowed_folders:
            folder_path = self.models_path / folder
            if folder_path.exists():
                safetensors_files.extend(list(folder_path.rglob("*.safetensors")))
        
        if not safetensors_files:
            print("未找到任何.safetensors文件")
            return
        
        print(f"找到 {len(safetensors_files)} 个模型文件")
        total = len(safetensors_files)
        processed = 0
        
        for file_path in safetensors_files:
            print(f"\n处理文件: {file_path.name}")
            try:
                current_mtime = os.path.getmtime(file_path)
                existing_info = self.models_info.get(str(file_path), {})
                
                # 检查文件是否已经扫描过且未修改
                if existing_info and existing_info.get("info", {}).get("mtime") == current_mtime:
                    print(f"文件 {file_path.name} 未修改，跳过扫描")
                    processed += 1
                    yield f"data: {json.dumps({'progress': processed / total, 'message': f'跳过: {file_path.name}'})}\n\n"
                    continue
                
                model_hash = await self.hash_utils.calculate_model_hash_async(file_path)
                print(f"计算得到哈希值: {model_hash}")
                await self.fetch_model_info(model_hash, file_path, current_mtime)
                self.save_models_info()  # 每次获取新信息后保存
                processed += 1
                yield f"data: {json.dumps({'progress': processed / total, 'message': f'已处理: {file_path.name}'})}\n\n"
            except Exception as e:
                print(f"处理文件 {file_path.name} 时发生错误: {str(e)}")
                processed += 1
                yield f"data: {json.dumps({'progress': processed / total, 'message': f'错误: {file_path.name}'})}\n\n"
            
    async def fetch_model_info(self, model_hash, file_path, mtime: float):
        """从Civitai API获取模型信息并下载预览图"""
        try:
            response = requests.get(f"{self.api_base_url}/model-versions/by-hash/{model_hash}")
            if response.status_code == 200:
                model_info = response.json()
                
                # 下载预览图
                preview_url = model_info.get("images", [{}])[0].get("url")
                if preview_url:
                    local_preview = await self.download_image(preview_url)
                    if local_preview:
                        model_info = {
                            **model_info,
                            "local_preview": local_preview,
                            "mtime": mtime,  # 记录文件修改时间
                            "scan_time": time.time()  # 记录扫描时间
                        }
                
                self.models_info[str(file_path)] = {
                    "hash": model_hash,
                    "info": model_info
                }
                print(f"成功获取模型信息: {file_path.name}")
            else:
                print(f"无法获取模型信息: {file_path.name}, 状态码: {response.status_code}")
        except Exception as e:
            print(f"获取模型信息时出错: {file_path.name}, 错误: {str(e)}")
    
    def save_models_info(self, output_file="models_info.json"):
        """保存模型信息到JSON文件"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.models_info, f, ensure_ascii=False, indent=2)
            
    def load_models_info(self, input_file="models_info.json"):
        """从JSON文件加载模型信息"""
        if os.path.exists(input_file):
            with open(input_file, "r", encoding="utf-8") as f:
                self.models_info = json.load(f)
            # 清理不存在的模型
            self._clean_nonexistent_models()

    def _clean_nonexistent_models(self):
        """清理不存在的模型信息"""
        to_remove = []
        for model_path in self.models_info.keys():
            if not os.path.exists(model_path):
                to_remove.append(model_path)
                # 清理相关的本地图片
                model_info = self.models_info[model_path]
                if "local_preview" in model_info.get("info", {}):
                    image_path = Path("static") / model_info["info"]["local_preview"].lstrip("/static/")
                    if image_path.exists():
                        image_path.unlink()
        
        # 从字典中移除不存在的模型
        for path in to_remove:
            del self.models_info[path]
        
        # 如果有清理，保存更新后的信息
        if to_remove:
            self.save_models_info()
            print(f"已清理 {len(to_remove)} 个不存在的模型")

    async def download_image(self, url: str) -> str:
        """下载图片并返回本地路径"""
        if not url:
            return None
            
        # 从URL中提取文件名
        filename = Path(urlparse(url).path).name
        local_path = self.images_path / filename
        
        # 如果文件已存在，直接返回路径
        if local_path.exists():
            return f"/static/images/{filename}"
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        async with aiofiles.open(local_path, 'wb') as f:
                            await f.write(await response.read())
                        return f"/static/images/{filename}"
        except Exception as e:
            print(f"下载图片失败: {url}, 错误: {str(e)}")
            return None
            
        return None

    def get_model_display_info(self, model_path: str) -> dict:
        """获取用于显示的模型信息"""
        model_info = self.models_info.get(model_path, {})
        if not model_info:
            return {
                "name": Path(model_path).name,
                "hash": "未知",
                "type": "未知",
                "preview_url": None,
                "description": "未找到模型信息",
                "baseModel": "未知",
                "nsfw": False,
                "nsfwLevel": 0,
            }
        
        info = model_info.get("info", {})
        model_data = info.get("model", {})
        preview_image = info.get("images", [{}])[0] if info.get("images") else {}
        preview_url = preview_image.get("url")
        
        # 添加本地图片路径
        local_preview = info.get("local_preview")
        
        return {
            "name": model_data.get("name", Path(model_path).name),
            "type": model_data.get("type", "未知"),
            "preview_url": local_preview or preview_url,
            "baseModel": info.get("baseModel", "未知"),
            "url": f"https://civitai.com/models/{info['modelId']}?modelVersionId={info['id']}",
            "nsfw": model_data.get("nsfw", False),
            "nsfwLevel": preview_image.get("nsfwLevel", 0),
        }

    def get_all_models_info(self) -> list:
        """获取所有模型的显示信息"""
        current_path = str(self.models_path)
        return [
            {
                "path": model_path,
                **self.get_model_display_info(model_path)
            }
            for model_path in self.models_info.keys()
            if str(model_path).startswith(current_path)
        ] 