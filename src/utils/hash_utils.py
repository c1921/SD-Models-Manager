import hashlib
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

class HashUtils:
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor()

    def calculate_model_hash(self, file_path: Path) -> str:
        """计算模型文件的SHA256哈希值"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    async def calculate_model_hash_async(self, file_path: Path) -> str:
        """异步计算模型文件的哈希值"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, self.calculate_model_hash, file_path) 