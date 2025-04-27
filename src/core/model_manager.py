import os
import json
import requests
from pathlib import Path
from typing import Dict, Any
import aiohttp
import aiofiles
from urllib.parse import urlparse
import time
import asyncio
from aiohttp import ClientTimeout

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
        # 设置数据目录和模型信息文件路径
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)  # 确保数据目录存在
        self.models_info_file = self.data_dir / "models_info.json"
        self.hash_utils = HashUtils()
        # 添加并发限制和超时设置
        self.semaphore = asyncio.Semaphore(5)  # 限制并发请求数
        self.timeout = ClientTimeout(total=10)  # 10秒超时
        # 添加自定义NSFW模型ID列表
        self.custom_nsfw_models = self.config.get("custom_nsfw_models", [])
        
    def load_config(self) -> dict:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"models_path": "", "output_file": "models_info.json", "custom_nsfw_models": []}
    
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
        
        # 先清理不存在的模型
        self._clean_nonexistent_models()
        
        # 只扫描 checkpoints 和 loras 文件夹
        allowed_folders = ['checkpoints', 'loras']
        safetensors_files = []
        
        for folder in allowed_folders:
            folder_path = self.models_path / folder
            if folder_path.exists():
                safetensors_files.extend(list(folder_path.rglob("*.safetensors")))
        
        if not safetensors_files:
            print("未找到任何.safetensors文件")
            yield f"data: {json.dumps({'progress': 1, 'message': '未找到任何模型文件', 'status': 'completed'})}\n\n"
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
                    # 计算精确的进度：已处理的数量 / 总数量
                    progress = processed / total
                    yield f"data: {json.dumps({'progress': progress, 'message': f'跳过: {file_path.name}'})}\n\n"
                    continue
                
                model_hash = await self.hash_utils.calculate_model_hash_async(file_path)
                print(f"计算得到哈希值: {model_hash}")
                await self.fetch_model_info(model_hash, file_path, current_mtime)
                self.save_models_info()  # 每次获取新信息后保存
                processed += 1
                # 计算精确的进度：已处理的数量 / 总数量
                progress = processed / total
                yield f"data: {json.dumps({'progress': progress, 'message': f'已处理: {file_path.name}'})}\n\n"
            except Exception as e:
                print(f"处理文件 {file_path.name} 时发生错误: {str(e)}")
                processed += 1
                # 计算精确的进度：已处理的数量 / 总数量
                progress = processed / total
                yield f"data: {json.dumps({'progress': progress, 'message': f'错误: {file_path.name}'})}\n\n"
        
        # 确保最后一个消息是完成状态，但不需要额外的100%消息了
        if processed == total:
            yield f"data: {json.dumps({'progress': 1, 'message': '扫描完成', 'status': 'completed'})}\n\n"
    
    async def fetch_model_info(self, model_hash, file_path, mtime: float):
        """从Civitai API获取模型信息并下载预览图"""
        async with self.semaphore:  # 使用信号量限制并发
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(f"{self.api_base_url}/model-versions/by-hash/{model_hash}") as response:
                        if response.status == 200:
                            model_info = await response.json()
                            
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
                            print(f"无法获取模型信息: {file_path.name}, 状态码: {response.status}")
            except Exception as e:
                print(f"获取模型信息时出错: {file_path.name}, 错误: {str(e)}")
    
    def save_models_info(self):
        """保存模型信息到JSON文件"""
        try:
            with open(self.models_info_file, "w", encoding="utf-8") as f:
                json.dump(self.models_info, f, ensure_ascii=False, indent=2)
            print(f"模型信息已保存到: {self.models_info_file}")
        except Exception as e:
            print(f"保存模型信息失败: {str(e)}")
            
    def load_models_info(self):
        """从JSON文件加载模型信息"""
        try:
            if self.models_info_file.exists():
                with open(self.models_info_file, "r", encoding="utf-8") as f:
                    self.models_info = json.load(f)
                print(f"已从 {self.models_info_file} 加载模型信息")
            else:
                self.models_info = {}
                print(f"模型信息文件 {self.models_info_file} 不存在，已初始化空数据")
        except Exception as e:
            print(f"加载模型信息失败: {str(e)}")
            self.models_info = {}

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
            
        max_retries = 3
        retry_delay = 1
        
        try:
            for attempt in range(max_retries):
                try:
                    async with aiohttp.ClientSession(timeout=self.timeout) as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                async with aiofiles.open(local_path, 'wb') as f:
                                    await f.write(await response.read())
                                return f"/static/images/{filename}"
                    break  # 如果成功就跳出重试循环
                except Exception as e:
                    if attempt < max_retries - 1:  # 如果不是最后一次尝试
                        await asyncio.sleep(retry_delay * (attempt + 1))  # 指数退避
                        continue
                    raise  # 最后一次尝试失败，抛出异常
        except Exception as e:
            print(f"下载图片失败: {url}, 错误: {str(e)}")
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
                "nsfw": str(model_path) in self.custom_nsfw_models,  # 检查是否在自定义NSFW列表中
                "custom_nsfw": str(model_path) in self.custom_nsfw_models,  # 新增自定义NSFW标记
                "original_nsfw": False,  # 新增原始NSFW标记
                "nsfwLevel": 0,
            }
        
        info = model_info.get("info", {})
        model_data = info.get("model", {})
        preview_image = info.get("images", [{}])[0] if info.get("images") else {}
        preview_url = preview_image.get("url")
        
        # 添加本地图片路径
        local_preview = info.get("local_preview")
        
        # 如果在自定义NSFW列表中，覆盖API返回的nsfw值
        is_custom_nsfw = str(model_path) in self.custom_nsfw_models
        is_original_nsfw = model_data.get("nsfw", False)
        
        return {
            "name": model_data.get("name", Path(model_path).name),
            "type": model_data.get("type", "未知"),
            "preview_url": local_preview or preview_url,
            "baseModel": info.get("baseModel", "未知"),
            "url": f"https://civitai.com/models/{info['modelId']}?modelVersionId={info['id']}" if 'modelId' in info and 'id' in info else None,
            "nsfw": is_custom_nsfw or is_original_nsfw,  # 自定义NSFW或API返回的NSFW
            "custom_nsfw": is_custom_nsfw,  # 新增自定义NSFW标记
            "original_nsfw": is_original_nsfw,  # 新增原始NSFW标记
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

    def toggle_custom_nsfw(self, model_path: str) -> bool:
        """切换模型的自定义NSFW状态
        
        Args:
            model_path: 模型路径
            
        Returns:
            bool: 更新后的NSFW状态
        """
        model_path = str(model_path)  # 确保为字符串
        
        # 检查是否为原始NSFW模型
        model_info = self.models_info.get(model_path, {})
        if model_info:
            info = model_info.get("info", {})
            model_data = info.get("model", {})
            is_original_nsfw = model_data.get("nsfw", False)
            
            # 如果是原始NSFW模型，不允许更改
            if is_original_nsfw:
                return True  # 保持NSFW状态
        
        if model_path in self.custom_nsfw_models:
            # 如果模型已在自定义NSFW列表中，则移除
            self.custom_nsfw_models.remove(model_path)
            current_state = False
        else:
            # 否则添加到列表中
            self.custom_nsfw_models.append(model_path)
            current_state = True
            
        # 更新配置并保存
        self.config["custom_nsfw_models"] = self.custom_nsfw_models
        self.save_config()
        
        return current_state 

    def get_default_settings(self):
        """获取默认设置"""
        return {"models_path": "", "output_file": str(self.models_info_file), "custom_nsfw_models": []} 