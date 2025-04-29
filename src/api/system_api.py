from fastapi import APIRouter, BackgroundTasks
import sys
import time
import os
import platform
import logging
import subprocess

router = APIRouter(prefix="/api/system", tags=["system"])
logger = logging.getLogger(__name__)

@router.post("/restart")
async def restart_application(background_tasks: BackgroundTasks):
    """重启应用程序"""
    logger.info("应用程序重启请求已接收")
    
    # 添加延迟重启任务到后台任务
    background_tasks.add_task(delayed_restart)
    
    return {"success": True, "message": "应用正在重启"}
    
def delayed_restart():
    """延迟重启应用程序，确保响应能够返回"""
    # 等待3秒确保响应已经发送
    time.sleep(3)
    logger.info("正在重启应用程序...")
    
    try:
        # 获取当前进程ID
        pid = os.getpid()
        logger.info(f"当前进程ID: {pid}")
        
        # 根据操作系统执行重启
        system = platform.system()
        
        if system == "Windows":
            # Windows系统
            # 获取当前Python解释器路径和执行脚本
            python_exe = sys.executable
            main_script = sys.argv[0]
            logger.info(f"Python解释器: {python_exe}")
            logger.info(f"主脚本: {main_script}")
            
            # 使用subprocess启动新进程
            cmd = f'start "" "{python_exe}" "{main_script}"'
            subprocess.Popen(cmd, shell=True)
            
            # 终止当前进程
            os._exit(0)
        else:
            # Linux/MacOS系统
            python_exe = sys.executable
            main_script = sys.argv[0]
            
            # 使用nohup确保进程在后台运行
            cmd = f'nohup {python_exe} {main_script} > /dev/null 2>&1 &'
            subprocess.Popen(cmd, shell=True)
            
            # 终止当前进程
            os._exit(0)
    except Exception as e:
        logger.error(f"重启应用程序时出错: {str(e)}")
        # 重启失败不要退出 