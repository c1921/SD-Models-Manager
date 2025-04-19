from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from pathlib import Path
from src.utils.file_utils import select_directory
from src.version.version import VERSION_STR, COMPANY, COPYRIGHT

class PathUpdate(BaseModel):
    path: str

def create_api(manager, frontend_url=None):
    """创建并配置FastAPI应用
    
    Args:
        manager: ModelManager实例
        frontend_url: 可选的前端URL，如果提供，根路径将重定向到此URL
    """
    app = FastAPI(title="Stable Diffusion 模型管理器")

    # 配置 CORS - 允许前端开发服务器的跨域请求
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载静态文件目录
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    else:
        # 如果目录不存在，创建它
        os.makedirs("static/images", exist_ok=True)
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # 检查是否存在前端构建文件
    frontend_paths = [
        "frontend/dist",  # 开发环境中的前端构建
        "frontend",       # PyInstaller打包后的前端文件
    ]
    
    frontend_dir = None
    for path in frontend_paths:
        if os.path.exists(path) and os.path.isdir(path):
            frontend_dir = path
            print(f"发现前端构建文件: {path}")
            break
    
    # 如果找到前端构建文件，挂载它
    if frontend_dir:
        app.mount("/assets", StaticFiles(directory=f"{frontend_dir}/assets"), name="frontend_assets")
        
        @app.get("/")
        async def read_root():
            """根路径，如果有前端构建文件，提供index.html"""
            return FileResponse(f"{frontend_dir}/index.html")
            
        @app.get("/favicon.svg")
        async def get_favicon():
            """提供favicon.svg文件"""
            # 检查前端目录中是否有favicon.svg
            frontend_favicon = f"{frontend_dir}/favicon.svg"
            if os.path.exists(frontend_favicon):
                return FileResponse(frontend_favicon)
                
            # 检查static目录
            static_favicon = "static/favicon.svg"
            if os.path.exists(static_favicon):
                return FileResponse(static_favicon)
                
            # 如果都没有，返回一个默认响应
            return JSONResponse(
                status_code=404,
                content={"detail": "Favicon not found"}
            )
    else:
        @app.get("/")
        async def read_root():
            """API根路径，返回API状态和版本信息"""
            # 如果指定了外部前端URL，则重定向
            if frontend_url:
                return RedirectResponse(url=frontend_url)
                
            # 否则返回API信息
            return {
                "status": "ok",
                "version": VERSION_STR,
                "app": "Stable Diffusion Models Manager API"
            }
            
        @app.get("/favicon.svg")
        async def get_favicon():
            """提供favicon.svg文件"""
            # 检查static目录
            static_favicon = "static/favicon.svg"
            if os.path.exists(static_favicon):
                return FileResponse(static_favicon)
                
            # 如果没有，返回一个默认响应
            return JSONResponse(
                status_code=404,
                content={"detail": "Favicon not found"}
            )

    @app.get("/api/models")
    async def get_models():
        """获取所有模型信息"""
        return manager.get_all_models_info()

    @app.post("/api/path")
    async def update_path(path_update: PathUpdate):
        """更新模型路径"""
        if not os.path.exists(path_update.path):
            raise HTTPException(status_code=400, detail="路径不存在")
        manager.update_models_path(path_update.path)
        return {"message": "路径已更新", "path": path_update.path}

    @app.get("/api/scan")
    async def scan_models_endpoint():
        """扫描模型"""
        if not manager.models_path or not os.path.exists(manager.models_path):
            raise HTTPException(status_code=400, detail="请先设置有效的模型目录路径")
        try:
            return StreamingResponse(
                manager.scan_models(),
                media_type="text/event-stream"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/config")
    async def get_config():
        """获取当前配置"""
        return {
            "models_path": str(manager.models_path) if manager.models_path else "",
            "is_path_valid": os.path.exists(manager.models_path) if manager.models_path else False
        }

    @app.get("/api/select-path")
    async def select_path_endpoint():
        """选择目录"""
        try:
            path = await select_directory()
            if path:
                # 如果选择了有效路径，立即更新
                manager.update_models_path(path)
                return {"path": path, "updated": True}
            return {"path": "", "updated": False, "detail": "未选择任何目录"}
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"path": "", "updated": False, "detail": f"选择目录失败: {str(e)}"}
            )

    @app.get("/api/version")
    async def get_version():
        """获取应用版本信息"""
        return {
            "version": VERSION_STR,
            "company": COMPANY,
            "copyright": COPYRIGHT
        }

    return app 