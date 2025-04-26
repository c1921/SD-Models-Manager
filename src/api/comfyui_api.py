import socket
import requests
import time
import os
import platform
import subprocess
from typing import Dict, Optional, List, Any
from fastapi import APIRouter, HTTPException, FastAPI

# ComfyUI默认端口和地址
COMFYUI_HOST = '127.0.0.1'
COMFYUI_PORT = 8188
COMFYUI_API_URL = f'http://{COMFYUI_HOST}:{COMFYUI_PORT}/api'

def create_comfyui_api():
    """创建ComfyUI相关API路由
    
    Returns:
        APIRouter: FastAPI路由对象
    """
    router = APIRouter()
    
    @router.get("/comfyui-status")
    async def check_comfyui_status():
        """检查ComfyUI是否在运行中
        
        Returns:
            dict: 包含status状态(running/stopped/unknown)和详细信息
        """
        try:
            # 尝试连接ComfyUI默认端口8188
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # 设置超时时间为1秒
            result = sock.connect_ex((COMFYUI_HOST, COMFYUI_PORT))
            sock.close()
            
            if result == 0:
                # 端口开放，ComfyUI正在运行
                # 尝试获取ComfyUI更详细的信息
                try:
                    response = requests.get(f'{COMFYUI_API_URL}/system_stats', timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "status": "running", 
                            "message": "ComfyUI 正在运行中",
                            "details": data
                        }
                except:
                    # 如果获取详细信息失败，仅返回运行状态
                    pass
                
                return {"status": "running", "message": "ComfyUI 正在运行中"}
            else:
                # 端口未开放，ComfyUI未运行
                return {"status": "stopped", "message": "ComfyUI 未运行"}
        except Exception as e:
            # 发生异常，无法确定状态
            return {"status": "unknown", "message": f"无法确定 ComfyUI 状态: {str(e)}"}
    
    @router.get("/comfyui-info")
    async def get_comfyui_info():
        """获取ComfyUI的详细信息
        
        Returns:
            dict: 包含ComfyUI的各种信息
        """
        try:
            # 先检查是否在运行
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((COMFYUI_HOST, COMFYUI_PORT))
            sock.close()
            
            if result != 0:
                raise HTTPException(status_code=503, detail="ComfyUI未运行")
                
            # 获取系统信息
            system_info = {}
            try:
                response = requests.get(f'{COMFYUI_API_URL}/system_stats', timeout=2)
                if response.status_code == 200:
                    system_info = response.json()
            except:
                system_info = {"error": "无法获取系统信息"}
                
            # 获取节点信息
            nodes_info = {}
            try:
                response = requests.get(f'{COMFYUI_API_URL}/object_info', timeout=2)
                if response.status_code == 200:
                    nodes_info = response.json()
            except:
                nodes_info = {"error": "无法获取节点信息"}
                
            return {
                "status": "running",
                "system_info": system_info,
                "nodes_count": len(nodes_info) if isinstance(nodes_info, dict) else 0,
                "api_url": COMFYUI_API_URL
            }
            
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取ComfyUI信息失败: {str(e)}")
    
    return router

def setup_comfyui_routes(app: FastAPI):
    """将ComfyUI API路由添加到FastAPI应用
    
    直接在main.py中调用此函数，无需经过model_api
    
    Args:
        app: FastAPI应用实例
    """
    comfyui_router = create_comfyui_api()
    app.include_router(comfyui_router, prefix="/api") 