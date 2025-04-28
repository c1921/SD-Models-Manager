from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from src.utils.file_utils import select_directory

class PathUpdate(BaseModel):
    path: str

class ModelIdParam(BaseModel):
    model_id: str

def create_api(manager):
    """创建并配置FastAPI应用
    
    Args:
        manager: ModelManager实例
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

    @app.get("/api/model-path")
    async def get_model_path():
        """获取模型目录"""
        path = str(manager.models_path) if manager.models_path else ""
        return {"path": path}

    @app.post("/api/toggle-nsfw")
    async def toggle_model_nsfw(model_param: ModelIdParam):
        """切换模型的NSFW状态"""
        try:
            new_state = manager.toggle_custom_nsfw(model_param.model_id)
            return {"success": True, "model_id": model_param.model_id, "nsfw": new_state}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"设置NSFW状态失败: {str(e)}")

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

    return app