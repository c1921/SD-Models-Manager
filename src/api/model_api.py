from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from src.utils.file_utils import select_directory
from src.version.version import VERSION_STR, COMPANY, COPYRIGHT

class PathUpdate(BaseModel):
    path: str

def create_api(manager):
    """创建并配置FastAPI应用"""
    app = FastAPI(title="Stable Diffusion 模型管理器")

    # 配置 CORS - 允许前端开发服务器的跨域请求
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 只挂载静态文件目录（用于图片等）
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    else:
        # 如果目录不存在，创建它
        os.makedirs("static/images", exist_ok=True)
        app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    async def read_root():
        """API根路径，返回API状态和版本信息"""
        return {
            "status": "ok",
            "version": VERSION_STR,
            "app": "Stable Diffusion Models Manager API"
        }

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
        return {"message": "路径已更新"}

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
        path = await select_directory()
        return {"path": path}

    @app.get("/api/version")
    async def get_version():
        """获取应用版本信息"""
        return {
            "version": VERSION_STR,
            "company": COMPANY,
            "copyright": COPYRIGHT
        }

    return app 