from fastapi import FastAPI
import os
from src.api.prompt_api import create_prompt_api
from src.api.prompt_library_api import create_prompt_library_api
from src.core.prompt_manager import PromptManager

def setup_prompt_routes(app: FastAPI):
    """设置提示词相关路由
    
    包括提示词翻译和提示词库管理
    
    Args:
        app: FastAPI应用实例
    """
    # 创建提示词管理器实例
    prompt_manager = PromptManager()
    
    # 集成提示词管理API
    prompt_router = create_prompt_api(prompt_manager)
    app.include_router(prompt_router, prefix="/api")

    # 集成提示词库API
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
    prompt_library_router = create_prompt_library_api(data_dir)
    app.include_router(prompt_library_router, prefix="/api") 