import os
import socket
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

async def select_directory() -> str:
    """使用文件对话框选择目录"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes('-topmost', True)  # 确保对话框在最前面
    path = filedialog.askdirectory()
    root.destroy()  # 完全清理 Tk 实例
    return path if path else ""

def find_free_port(start_port=8080, max_tries=100):
    """查找可用的端口号"""
    for port in range(start_port, start_port + max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError('无法找到可用的端口')

def get_file_mtime(file_path: Path) -> float:
    """获取文件的修改时间戳"""
    return os.path.getmtime(file_path) 