from fastapi import APIRouter
from src.version.version import VERSION_STR, COMPANY, COPYRIGHT

def create_common_api():
    """创建通用API路由
    
    用于项目整体的通用API，如版本信息、健康检查等
    
    Returns:
        APIRouter: FastAPI路由对象
    """
    router = APIRouter()
    
    @router.get("/version")
    async def get_version():
        """获取应用版本信息"""
        return {
            "version": VERSION_STR,
            "company": COMPANY,
            "copyright": COPYRIGHT
        }
    
    @router.get("/health")
    async def health_check():
        """应用健康检查"""
        return {
            "status": "ok",
            "service": "SD-Models-Manager"
        }
    
    return router

def setup_common_routes(app):
    """将通用API路由添加到FastAPI应用
    
    Args:
        app: FastAPI应用实例
    """
    common_router = create_common_api()
    app.include_router(common_router, prefix="/api")