#!/usr/bin/env python
"""
开发辅助脚本，同时启动后端API服务和前端Vite开发服务器
"""
import os
import subprocess
import sys
import time
import webbrowser
import signal
import platform
import argparse
from src.utils.file_utils import find_free_port

# 进程列表，用于在退出时关闭
processes = []

def is_windows():
    """检查是否是Windows系统"""
    return platform.system() == "Windows"

def start_backend(port):
    """启动后端API服务"""
    print(f"正在启动后端API服务 (端口: {port})...")
    
    # 设置环境变量
    env = os.environ.copy()
    
    # 构建命令
    cmd = [sys.executable, "main.py", "--port", str(port), "--no-browser"]
    
    # 启动后端进程
    if is_windows():
        # Windows使用CREATE_NEW_CONSOLE创建新的控制台窗口
        backend_process = subprocess.Popen(
            cmd,
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Unix系统使用新的进程组
        backend_process = subprocess.Popen(
            cmd,
            env=env,
            preexec_fn=os.setsid
        )
    
    processes.append(("backend", backend_process))
    print(f"后端API服务已启动，进程ID: {backend_process.pid}")
    
    # 等待一点时间确保服务已启动
    time.sleep(2)
    
    return backend_process

def start_frontend(api_port):
    """启动前端Vite开发服务器"""
    print("正在启动前端Vite开发服务器...")
    
    # 设置环境变量
    env = os.environ.copy()
    # 设置API端口环境变量，供Vite配置使用
    env["VITE_API_PORT"] = str(api_port)
    
    # 构建命令
    npm_cmd = "npm.cmd" if is_windows() else "npm"
    cmd = [npm_cmd, "run", "dev"]
    
    # 切换到前端目录
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    
    # 启动前端进程
    if is_windows():
        # Windows使用CREATE_NEW_CONSOLE创建新的控制台窗口
        frontend_process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Unix系统使用新的进程组
        frontend_process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            env=env,
            preexec_fn=os.setsid
        )
    
    processes.append(("frontend", frontend_process))
    print(f"前端开发服务器已启动，进程ID: {frontend_process.pid}")
    
    return frontend_process

def cleanup():
    """清理所有子进程"""
    print("\n正在关闭所有进程...")
    
    for name, process in processes:
        if process.poll() is None:  # 检查进程是否仍在运行
            print(f"正在关闭{name}进程 (PID: {process.pid})...")
            
            if is_windows():
                # Windows通过taskkill终止进程树
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
            else:
                # Unix发送SIGTERM到进程组
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except OSError:
                    process.terminate()
            
            # 等待进程终止
            try:
                process.wait(timeout=5)
                print(f"{name}进程已关闭")
            except subprocess.TimeoutExpired:
                print(f"无法正常关闭{name}进程，强制终止")
                process.kill()

def signal_handler(sig, frame):
    """信号处理函数，用于捕获Ctrl+C"""
    print("\n收到中断信号，准备退出...")
    cleanup()
    sys.exit(0)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='开发辅助脚本，同时启动后端和前端服务')
    parser.add_argument('--port', type=int, default=None, help='后端API端口')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    args = parser.parse_args()
    
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 获取可用端口
        api_port = args.port or find_free_port()
        
        # 启动后端服务
        backend_process = start_backend(api_port)
        
        # 启动前端服务
        frontend_process = start_frontend(api_port)
        
        # 等待一段时间后打开浏览器
        if not args.no_browser:
            print("等待1秒后将打开浏览器...")
            time.sleep(1)
            webbrowser.open("http://localhost:5173")
        
        print("\n开发环境已启动!")
        print(f"API服务地址: http://127.0.0.1:{api_port}")
        print("前端服务地址: http://localhost:5173")
        print("按Ctrl+C可同时关闭所有服务")
        
        # 等待后端进程结束
        while backend_process.poll() is None:
            time.sleep(1)
        
        # 如果后端终止，也关闭前端
        print("后端服务已终止，正在关闭前端服务...")
        cleanup()
        
    except KeyboardInterrupt:
        print("\n收到中断，正在关闭服务...")
        cleanup()
    except Exception as e:
        print(f"发生错误: {str(e)}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main() 