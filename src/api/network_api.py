from fastapi import APIRouter
import asyncio
from fastapi import FastAPI
from src.core.network_service import network_service

def create_network_api():
    """创建网络检测相关API路由
    
    Returns:
        APIRouter: FastAPI路由对象
    """
    router = APIRouter()
    
    @router.get("/network-status")
    async def check_network_status(force_refresh: bool = False):
        """检查网络连接状态
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            网络状态检测结果
        """
        return await network_service.get_status(force_refresh)
    
    return router

def setup_network_routes(app: FastAPI):
    """将网络API路由添加到FastAPI应用
    
    Args:
        app: FastAPI应用实例
    """
    network_router = create_network_api()
    app.include_router(network_router, prefix="/api")
    
    # 不再使用startup事件触发网络检测
    # 前端组件挂载时会触发检测，避免重复检测 