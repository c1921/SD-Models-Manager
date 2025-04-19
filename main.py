import argparse
import time
import webbrowser
import threading
import uvicorn
import os

from src.core.model_manager import ModelManager
from src.api.model_api import create_api
from src.utils.file_utils import find_free_port

def open_browser(url: str):
    """延迟一秒后打开浏览器"""
    time.sleep(1)
    webbrowser.open(url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='模型管理器')
    parser.add_argument('--port', type=int, default=None, help='API服务端口')
    parser.add_argument('--frontend', default=None, help='前端URL地址，如http://localhost:5173')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    args = parser.parse_args()

    # 获取可用端口
    port = args.port or find_free_port()
    
    # 前端URL，如果提供了--frontend参数，使用该地址
    frontend_url = args.frontend or f"http://localhost:{port}"

    # 创建 ModelManager 实例
    manager = ModelManager()
    
    # 加载已有的模型信息
    manager.load_models_info()
    
    # 创建 FastAPI 应用
    app = create_api(manager)
    
    # 在新线程中打开浏览器（如果未指定--no-browser）
    if not args.no_browser:
        # 打开指定的前端URL
        threading.Thread(target=open_browser, args=(frontend_url,), daemon=True).start()
    
    print(f"API服务运行在: http://127.0.0.1:{port}")
    if args.frontend:
        print(f"前端页面地址: {args.frontend}")
    else:
        print("未指定前端地址，将尝试在本地访问API服务")
        print("如果您使用Vue前端开发服务器，请使用以下命令:")
        print(f"python main.py --frontend http://localhost:5173 --no-browser")
    
    # 启动 FastAPI 服务器
    uvicorn.run(app, host="127.0.0.1", port=port) 