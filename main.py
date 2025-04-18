import argparse
import time
import webbrowser
import threading
import uvicorn
import os

from src.core.model_manager import ModelManager
from src.api.model_api import create_api
from src.utils.file_utils import find_free_port

def open_browser(port: int):
    """延迟一秒后打开浏览器"""
    time.sleep(1)
    webbrowser.open(f'http://127.0.0.1:{port}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='模型管理器')
    parser.add_argument('--port', type=int, default=None, help='Web界面端口')
    parser.add_argument('--dev', action='store_true', help='开发模式')
    args = parser.parse_args()

    # 设置开发模式环境变量
    if args.dev:
        os.environ["DEV_MODE"] = "1"
        print("正在以开发模式运行...")
    else:
        os.environ["DEV_MODE"] = "0"

    # 获取可用端口
    port = args.port or find_free_port()

    # 创建 ModelManager 实例
    manager = ModelManager()
    
    # 加载已有的模型信息
    manager.load_models_info()
    
    # 创建 FastAPI 应用
    app = create_api(manager)
    
    # 除非在开发模式下，否则在新线程中打开浏览器
    if not args.dev:
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    else:
        print(f"API服务运行在: http://127.0.0.1:{port}")
        print(f"前端开发服务器应运行在: http://localhost:5173")
        print(f"确保在frontend/vite.config.ts中的代理target配置为'http://127.0.0.1:{port}'")
    
    # 启动 FastAPI 服务器
    uvicorn.run(app, host="127.0.0.1", port=port) 