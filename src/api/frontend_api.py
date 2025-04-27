from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import os
import sys

def is_packaged():
    """检查应用是否使用PyInstaller打包"""
    # 通过检查是否有_MEIPASS属性判断是否被PyInstaller打包
    return hasattr(sys, '_MEIPASS')

def setup_frontend_routes(app: FastAPI, frontend_url=None):
    """设置前端相关路由和静态文件服务
    
    处理根路径、favicon、静态资源等
    
    Args:
        app: FastAPI应用实例
        frontend_url: 可选的外部前端URL，如果提供，根路径将重定向到此URL
    """
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
        if os.path.exists(path) and os.path.isdir(path) and os.path.exists(f"{path}/index.html"):
            frontend_dir = path
            print(f"发现前端构建文件: {path}")
            break
    
    # 如果找到前端构建文件，挂载它
    if frontend_dir:
        if os.path.exists(f"{frontend_dir}/assets") and os.path.isdir(f"{frontend_dir}/assets"):
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
        # 如果没有前端构建文件，但指定了外部前端URL
        if frontend_url:
            @app.get("/")
            async def read_root():
                """重定向到外部前端URL"""
                return RedirectResponse(url=frontend_url)
        else:
            # 既没有前端构建文件，也没有指定外部前端URL
            # 使用API模式
            from src.version.version import VERSION_STR
            
            @app.get("/")
            async def read_root():
                """API根路径，返回API状态信息"""
                return {
                    "status": "ok",
                    "app": "Stable Diffusion Models Manager API",
                    "mode": "API Only"
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