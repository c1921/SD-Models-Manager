from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import json
from datetime import datetime

# 提示词库项目模型
class PromptLibraryItem(BaseModel):
    id: str
    text: str
    chinese: str
    english: str
    category: str
    subCategory: str

# 创建提示词库项目请求
class CreatePromptLibraryItemRequest(BaseModel):
    text: str
    chinese: str
    english: str
    category: str
    subCategory: str

# 更新提示词库项目请求
class UpdatePromptLibraryItemRequest(BaseModel):
    text: Optional[str] = None
    chinese: Optional[str] = None
    english: Optional[str] = None
    category: Optional[str] = None
    subCategory: Optional[str] = None

# 提示词库管理类
class PromptLibraryManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.library_file = os.path.join(data_dir, "prompt_library.json")
        self.items = []
        self.load_library()

    def load_library(self):
        """加载提示词库"""
        try:
            if os.path.exists(self.library_file):
                with open(self.library_file, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
                print(f"已加载提示词库，共{len(self.items)}个项目")
            else:
                self.items = []
                print("提示词库文件不存在，已初始化空库")
        except Exception as e:
            print(f"加载提示词库失败: {str(e)}")
            self.items = []

    def save_library(self):
        """保存提示词库"""
        try:
            # 确保目录存在
            os.makedirs(self.data_dir, exist_ok=True)
            
            with open(self.library_file, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
            print(f"已保存提示词库，共{len(self.items)}个项目")
            return True
        except Exception as e:
            print(f"保存提示词库失败: {str(e)}")
            return False

    def get_all_items(self):
        """获取所有提示词库项目"""
        return self.items

    def add_item(self, item_data: CreatePromptLibraryItemRequest):
        """添加提示词库项目"""
        new_item = {
            "id": str(uuid.uuid4()),
            "text": item_data.text,
            "chinese": item_data.chinese,
            "english": item_data.english,
            "category": item_data.category,
            "subCategory": item_data.subCategory
        }
        
        # 检查是否已存在相同的项目
        if any(item["text"] == item_data.text for item in self.items):
            return None
            
        self.items.append(new_item)
        self.save_library()
        return new_item

    def update_item(self, item_id: str, item_data: UpdatePromptLibraryItemRequest):
        """更新提示词库项目"""
        for item in self.items:
            if item["id"] == item_id:
                if item_data.text is not None:
                    item["text"] = item_data.text
                if item_data.chinese is not None:
                    item["chinese"] = item_data.chinese
                if item_data.english is not None:
                    item["english"] = item_data.english
                if item_data.category is not None:
                    item["category"] = item_data.category
                if item_data.subCategory is not None:
                    item["subCategory"] = item_data.subCategory
                
                self.save_library()
                return item
        return None

    def delete_item(self, item_id: str):
        """删除提示词库项目"""
        for i, item in enumerate(self.items):
            if item["id"] == item_id:
                del self.items[i]
                self.save_library()
                return True
        return False

# 创建提示词库API
def create_prompt_library_api(data_dir):
    router = APIRouter()
    library_manager = PromptLibraryManager(data_dir)
    
    @router.get("/prompt-library")
    async def get_prompt_library():
        """获取提示词库列表"""
        try:
            items = library_manager.get_all_items()
            return {"items": items}
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"获取提示词库失败: {str(e)}"}
            )
    
    @router.post("/prompt-library")
    async def save_prompt_to_library(item: CreatePromptLibraryItemRequest):
        """保存提示词到库"""
        try:
            # 验证提示词必填字段
            if not item.text or not item.chinese or not item.english or not item.category:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "提示词、中英文翻译和分类不能为空"}
                )
                
            new_item = library_manager.add_item(item)
            if new_item:
                return new_item
            else:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "提示词已存在"}
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"保存提示词失败: {str(e)}"}
            )
    
    @router.put("/prompt-library/{item_id}")
    async def update_prompt_library_item(item_id: str, item: UpdatePromptLibraryItemRequest):
        """更新提示词库项目"""
        try:
            updated_item = library_manager.update_item(item_id, item)
            if updated_item:
                return updated_item
            else:
                return JSONResponse(
                    status_code=404,
                    content={"detail": "提示词不存在"}
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"更新提示词失败: {str(e)}"}
            )
    
    @router.delete("/prompt-library/{item_id}")
    async def delete_prompt_library_item(item_id: str):
        """删除提示词库项目"""
        try:
            result = library_manager.delete_item(item_id)
            if result:
                return {"success": True}
            else:
                return JSONResponse(
                    status_code=404,
                    content={"detail": "提示词不存在"}
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"删除提示词失败: {str(e)}"}
            )
    
    return router 