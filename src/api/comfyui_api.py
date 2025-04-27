import socket
import time
import os
import platform
import subprocess
import asyncio
import aiohttp
from typing import Dict, Optional, List, Any
from fastapi import APIRouter, HTTPException, FastAPI

# ComfyUI默认端口和地址
COMFYUI_HOST = '127.0.0.1'
COMFYUI_PORT = 8188
COMFYUI_API_URL = f'http://{COMFYUI_HOST}:{COMFYUI_PORT}/api'

async def is_port_open(host, port, timeout=1):
    """异步检测端口是否开放"""
    try:
        # 使用asyncio创建TCP连接
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, OSError):
        return False

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
            # 异步检测ComfyUI端口是否开放
            port_open = await is_port_open(COMFYUI_HOST, COMFYUI_PORT, timeout=0.5)
            
            if port_open:
                # 端口开放，ComfyUI正在运行
                # 尝试获取ComfyUI更详细的信息
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{COMFYUI_API_URL}/system_stats', timeout=2) as response:
                            if response.status == 200:
                                data = await response.json()
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
            # 异步检测ComfyUI是否在运行
            port_open = await is_port_open(COMFYUI_HOST, COMFYUI_PORT, timeout=0.5)
            
            if not port_open:
                raise HTTPException(status_code=503, detail="ComfyUI未运行")
                
            # 获取系统信息
            system_info = {}
            nodes_info = {}
            
            async with aiohttp.ClientSession() as session:
                # 异步获取系统信息
                try:
                    async with session.get(f'{COMFYUI_API_URL}/system_stats', timeout=2) as response:
                        if response.status == 200:
                            system_info = await response.json()
                except:
                    system_info = {"error": "无法获取系统信息"}
                
                # 异步获取节点信息
                try:
                    async with session.get(f'{COMFYUI_API_URL}/object_info', timeout=2) as response:
                        if response.status == 200:
                            nodes_info = await response.json()
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