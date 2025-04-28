import argparse
import time
import webbrowser
import threading
import uvicorn
import os
import sys
from pathlib import Path

from src.core.config_manager import ConfigManager
from src.core.model_manager import ModelManager
from src.api.model_api import create_api
from src.api.comfyui_api import setup_comfyui_routes
from src.api.network_api import setup_network_routes
from src.api.common_api import setup_common_routes
from src.api.frontend_api import setup_frontend_routes
from src.api.prompt_routes import setup_prompt_routes
from src.utils.file_utils import find_free_port

def open_browser(url: str):
    """延迟一秒后打开浏览器"""
    time.sleep(1)
    webbrowser.open(url)

def is_packaged():
    """检查应用是否使用PyInstaller打包"""
    # 通过检查是否有_MEIPASS属性判断是否被PyInstaller打包
    return hasattr(sys, '_MEIPASS')

def get_frontend_dir():
    """尝试找到前端构建目录"""
    # 检查可能的前端目录位置
    frontend_paths = [
        Path("frontend/dist"),  # 本地开发构建
        Path("frontend"),       # PyInstaller打包后
    ]
    
    for path in frontend_paths:
        if path.exists() and path.is_dir() and (path / "index.html").exists():
            return path
    
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='模型管理器')
    parser.add_argument('--port', type=int, default=None, help='API服务端口')
    parser.add_argument('--frontend', default=None, help='前端URL地址，如http://localhost:5173')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--dev', action='store_true', help='开发模式 (等同于 --frontend http://localhost:5173 --no-browser)')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    args = parser.parse_args()

    # 获取可用端口
    port = args.port or find_free_port()
    
    # 处理开发模式参数
    if args.dev:
        args.frontend = "http://localhost:5173"
        args.no_browser = True
    
    # 设置前端URL
    frontend_url = args.frontend
    
    # 如果没有指定前端URL，检查是否有前端构建
    if not frontend_url:
        frontend_dir = get_frontend_dir()
        if frontend_dir:
            # 使用API服务器提供前端文件
            frontend_url = f"http://127.0.0.1:{port}"
        else:
            # 没有前端，只使用API
            frontend_url = None
    
    # 创建配置管理器
    config_manager = ConfigManager(args.config)
    
    # 创建 ModelManager 实例，并传入配置管理器
    manager = ModelManager(args.config)
    
    # 加载已有的模型信息
    manager.load_models_info()
    
    # 创建 FastAPI 应用
    app = create_api(manager)
    
    # 设置前端路由(静态文件、根路径等)
    setup_frontend_routes(app, frontend_url=frontend_url)
    
    # 设置ComfyUI路由
    setup_comfyui_routes(app)
    
    # 设置网络检测路由
    setup_network_routes(app)
    
    # 设置通用API路由
    setup_common_routes(app)
    
    # 设置提示词相关路由
    setup_prompt_routes(app)
    
    # 在新线程中打开浏览器（如果未指定--no-browser）
    if not args.no_browser and frontend_url:
        threading.Thread(target=open_browser, args=(frontend_url,), daemon=True).start()
    
    # 打印服务信息
    print(f"API服务运行在: http://127.0.0.1:{port}")
    
    if frontend_url:
        if frontend_url == f"http://127.0.0.1:{port}":
            print("前端页面与API服务在同一地址")
        else:
            print(f"前端页面地址: {frontend_url}")
    else:
        print("未检测到前端，以纯API模式运行")
    
    # 启动 FastAPI 服务器
    uvicorn.run(app, host="127.0.0.1", port=port)