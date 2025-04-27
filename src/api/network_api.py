from fastapi import APIRouter
import asyncio
import aiohttp
import time
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks

# 检测目标配置
NETWORK_TARGETS = {
    "civitai": {
        "name": "Civitai API",
        "url": "https://civitai.com/api/v1/models",
        "timeout": 5
    },
    "google_translate": {
        "name": "Google 翻译",
        "url": "https://translate.google.com",
        "timeout": 5
    }
}

# 缓存检测结果，避免频繁请求
CACHE_DURATION = 300  # 缓存有效期5分钟
network_status_cache = {
    "last_check": 0,
    "results": {}
}

async def check_url_availability(url: str, timeout: int = 5) -> Dict[str, Any]:
    """异步检查URL是否可访问

    Args:
        url: 目标URL
        timeout: 超时时间（秒）

    Returns:
        检测结果，包含状态和响应时间
    """
    start_time = time.time()
    
    try:
        # 使用aiohttp发起请求
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                elapsed = time.time() - start_time
                
                return {
                    "available": response.status < 400,  # 2xx或3xx状态码视为可用
                    "status_code": response.status,
                    "response_time": round(elapsed * 1000),  # 毫秒
                    "message": "连接成功" if response.status < 400 else f"状态码错误: {response.status}"
                }
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        return {
            "available": False,
            "status_code": None,
            "response_time": round(elapsed * 1000),
            "message": f"连接超时 (>{timeout}秒)"
        }
    except aiohttp.ClientError as e:
        elapsed = time.time() - start_time
        return {
            "available": False,
            "status_code": None,
            "response_time": round(elapsed * 1000),
            "message": f"连接错误: {str(e)}"
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "available": False,
            "status_code": None,
            "response_time": round(elapsed * 1000),
            "message": f"未知错误: {str(e)}"
        }

async def run_network_check():
    """在后台运行网络检测"""
    global network_status_cache
    
    print("执行初始网络状态检测...")
    
    # 执行新的检测
    tasks = {}
    for target_id, target in NETWORK_TARGETS.items():
        # 为每个目标创建检测任务
        tasks[target_id] = check_url_availability(
            target["url"], 
            target["timeout"]
        )
    
    # 并行执行所有任务
    results = {}
    for target_id, task in tasks.items():
        try:
            result = await task
            results[target_id] = {
                "name": NETWORK_TARGETS[target_id]["name"],
                "url": NETWORK_TARGETS[target_id]["url"],
                "result": result
            }
        except Exception as e:
            print(f"检测 {target_id} 失败: {str(e)}")
            results[target_id] = {
                "name": NETWORK_TARGETS[target_id]["name"],
                "url": NETWORK_TARGETS[target_id]["url"],
                "result": {
                    "available": False,
                    "status_code": None,
                    "response_time": 0,
                    "message": f"检测过程出错: {str(e)}"
                }
            }
    
    # 更新缓存
    network_status_cache = {
        "last_check": time.time(),
        "results": results
    }
    
    print("初始网络状态检测完成")

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
        global network_status_cache
        
        current_time = time.time()
        # 如果缓存有效且不是强制刷新，则返回缓存
        if (not force_refresh and 
            current_time - network_status_cache["last_check"] < CACHE_DURATION and 
            network_status_cache["results"]):
            
            return {
                "status": "cached",
                "last_check": network_status_cache["last_check"],
                "results": network_status_cache["results"]
            }
        
        # 否则执行新的检测
        tasks = {}
        for target_id, target in NETWORK_TARGETS.items():
            # 为每个目标创建检测任务
            tasks[target_id] = check_url_availability(
                target["url"], 
                target["timeout"]
            )
        
        # 并行执行所有任务
        results = {}
        for target_id, task in tasks.items():
            results[target_id] = {
                "name": NETWORK_TARGETS[target_id]["name"],
                "url": NETWORK_TARGETS[target_id]["url"],
                "result": await task
            }
        
        # 更新缓存
        network_status_cache = {
            "last_check": current_time,
            "results": results
        }
        
        return {
            "status": "fresh",
            "last_check": current_time,
            "results": results
        }
    
    return router

def setup_network_routes(app: FastAPI):
    """将网络API路由添加到FastAPI应用
    
    Args:
        app: FastAPI应用实例
    """
    network_router = create_network_api()
    app.include_router(network_router, prefix="/api")
    
    # 在启动事件中添加初始网络检测
    @app.on_event("startup")
    async def startup_network_check():
        # 在后台运行网络检测，不阻塞应用启动
        background_tasks = BackgroundTasks()
        background_tasks.add_task(run_network_check)
        await run_network_check()  # 直接运行一次，确保有初始数据 