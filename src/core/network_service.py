import asyncio
import aiohttp
import time
from typing import Dict, Any

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

class NetworkService:
    """网络状态检测服务类"""
    
    def __init__(self):
        """初始化网络检测服务"""
        self.network_status_cache = {
            "last_check": 0,
            "results": {}
        }
        # 添加锁，避免重复检测
        self._check_lock = asyncio.Lock()
        # 标记是否正在检测中
        self._checking = False
    
    async def check_url_availability(self, url: str, timeout: int = 5) -> Dict[str, Any]:
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
    
    async def run_network_check(self):
        """执行网络检测"""
        # 使用锁和标记避免重复检测
        if self._checking:
            print("网络检测已在进行中，跳过本次检测")
            return self.network_status_cache.get("results", {})
            
        # 尝试获取锁
        if not await self._check_lock.acquire():
            print("无法获取检测锁，跳过本次检测")
            return self.network_status_cache.get("results", {})
            
        # 标记检测开始
        self._checking = True
        print("执行网络状态检测...")
        
        try:
            # 准备所有检测任务
            tasks = []
            for target_id, target in NETWORK_TARGETS.items():
                task = self.check_url_availability(target["url"], target["timeout"])
                tasks.append((target_id, task))
            
            # 并行执行所有任务
            results = {}
            for target_id, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=NETWORK_TARGETS[target_id]["timeout"]+1)
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
            self.network_status_cache = {
                "last_check": time.time(),
                "results": results
            }
            
            print("网络状态检测完成")
            return results
        except Exception as e:
            print(f"网络状态检测失败: {str(e)}")
            # 确保即使发生错误也更新缓存
            self.network_status_cache = {
                "last_check": time.time(),
                "results": {}
            }
            return {}
        finally:
            # 标记检测结束，释放锁
            self._checking = False
            self._check_lock.release()
    
    async def get_status(self, force_refresh: bool = False):
        """获取网络状态
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            网络状态检测结果
        """
        current_time = time.time()
        # 如果缓存有效且不是强制刷新，则返回缓存
        if (not force_refresh and 
            current_time - self.network_status_cache["last_check"] < CACHE_DURATION and 
            self.network_status_cache["results"]):
            
            return {
                "status": "cached",
                "last_check": self.network_status_cache["last_check"],
                "results": self.network_status_cache["results"]
            }
        
        # 强制刷新或缓存过期时，执行新的检测
        # 优先使用run_network_check方法进行检测（包含锁机制）
        if force_refresh or not self.network_status_cache["results"]:
            results = await self.run_network_check()
            
            return {
                "status": "fresh",
                "last_check": self.network_status_cache["last_check"],
                "results": self.network_status_cache["results"]
            }
        
        # 使用缓存
        return {
            "status": "cached",
            "last_check": self.network_status_cache["last_check"],
            "results": self.network_status_cache["results"]
        }

# 创建全局网络服务实例
network_service = NetworkService() 