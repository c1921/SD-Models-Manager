import os
import json
import requests
from pathlib import Path
import hashlib
import argparse
import yaml
from nicegui import ui, app
from typing import Dict, Any
import asyncio
from datetime import datetime

class ModelManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.models_path = Path(self.config.get("models_path", ""))
        self.api_base_url = "https://civitai.com/api/v1"
        self.models_info: Dict[str, Any] = {}
        
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
    
    def calculate_model_hash(self, file_path):
        """计算模型文件的SHA256哈希值"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def scan_models(self):
        """扫描指定目录下的所有.safetensors文件"""
        print(f"开始扫描目录: {self.models_path}")
        safetensors_files = list(self.models_path.rglob("*.safetensors"))
        
        if not safetensors_files:
            print("未找到任何.safetensors文件")
            return
        
        print(f"找到 {len(safetensors_files)} 个模型文件")
        
        for file_path in safetensors_files:
            print(f"\n处理文件: {file_path.name}")
            try:
                model_hash = self.calculate_model_hash(file_path)
                print(f"计算得到哈希值: {model_hash}")
                self.fetch_model_info(model_hash, file_path)
            except Exception as e:
                print(f"处理文件 {file_path.name} 时发生错误: {str(e)}")
            
    def fetch_model_info(self, model_hash, file_path):
        """从Civitai API获取模型信息"""
        try:
            response = requests.get(f"{self.api_base_url}/model-versions/by-hash/{model_hash}")
            if response.status_code == 200:
                model_info = response.json()
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
                "download_count": 0,
                "rating": 0,
            }
        
        info = model_info.get("info", {})
        model_data = info.get("model", {})
        
        return {
            "name": model_data.get("name", Path(model_path).name),
            "hash": model_info.get("hash", "未知"),
            "type": model_data.get("type", "未知"),
            "preview_url": info.get("images", [{}])[0].get("url") if info.get("images") else None,
            "description": model_data.get("description", "无描述"),
            "download_count": model_data.get("downloadCount", 0),
            "rating": model_data.get("rating", 0),
        }

def create_ui(manager: ModelManager):
    @ui.page('/')
    def home():
        with ui.header().classes('bg-blue-600 text-white'):
            ui.label('Stable Diffusion 模型管理器').classes('text-h6')
        
        with ui.row().classes('w-full p-4'):
            path_input = ui.input(
                label='模型目录路径', 
                value=str(manager.models_path),
                placeholder='请输入模型目录路径'
            ).classes('w-96')
            
            async def save_path():
                new_path = path_input.value
                if not new_path:
                    ui.notify('请输入有效的路径', color='warning')
                    return
                if not os.path.exists(new_path):
                    ui.notify('路径不存在', color='negative')
                    return
                manager.update_models_path(new_path)
                ui.notify('路径已保存', color='positive')
                app.reload()  # 重新加载页面
            
            ui.button('保存路径', on_click=save_path).classes('bg-green-500 text-white')
            
            loading_label = ui.label('').classes('text-blue-500')
            refresh_btn = ui.button('刷新模型', on_click=None).classes('bg-blue-500 text-white')
            
            async def refresh_models():
                if not manager.models_path or not os.path.exists(manager.models_path):
                    ui.notify('请先设置有效的模型目录路径', color='warning')
                    return
                
                refresh_btn.disable()
                loading_label.text = '正在扫描模型...'
                
                try:
                    await asyncio.to_thread(manager.scan_models)
                    await asyncio.to_thread(manager.save_models_info)
                    ui.notify('模型扫描完成')
                    app.reload()  # 重新加载页面以显示新数据
                finally:
                    loading_label.text = ''
                    refresh_btn.enable()
            
            refresh_btn.on_click(refresh_models)
        
        if not manager.models_path or not os.path.exists(manager.models_path):
            ui.label('请先设置模型目录路径').classes('text-red-500 p-4')
            return
            
        with ui.grid(columns=3).classes('gap-4 p-4'):
            for model_path, _ in manager.models_info.items():
                model_info = manager.get_model_display_info(model_path)
                with ui.card().classes('w-full'):
                    if model_info['preview_url']:
                        ui.image(model_info['preview_url']).classes('w-full h-48 object-cover')
                    
                    with ui.card_section():
                        ui.label(model_info['name']).classes('text-h6')
                        ui.label(f"类型: {model_info['type']}")
                        ui.label(f"下载次数: {model_info['download_count']}")
                        ui.label(f"评分: {model_info['rating']}")
                        
                    with ui.expansion('详细信息', icon='info'):
                        ui.label(f"哈希值: {model_info['hash']}")
                        ui.markdown(model_info['description'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='模型管理器')
    parser.add_argument('--port', type=int, default=8080, help='Web界面端口')
    args = parser.parse_args()

    manager = ModelManager()
    
    # 加载已有的模型信息
    manager.load_models_info()
    
    # 创建Web界面
    create_ui(manager)
    
    # 启动服务器
    ui.run(port=args.port, reload=False) 