import argparse
import time
import webbrowser
import threading
import uvicorn

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
    args = parser.parse_args()

    # 获取可用端口
    port = args.port or find_free_port()

    # 创建 ModelManager 实例
    manager = ModelManager()
    
    # 加载已有的模型信息
    manager.load_models_info()
    
    # 创建 FastAPI 应用
    app = create_api(manager)
    
    # 在新线程中打开浏览器
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    # 启动 FastAPI 服务器
    uvicorn.run(app, host="127.0.0.1", port=port) 