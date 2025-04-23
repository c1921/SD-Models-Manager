from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PromptCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: Optional[List[str]] = None
    auto_translate: Optional[bool] = True

class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    auto_translate: Optional[bool] = True

class TranslateRequest(BaseModel):
    text: str
    to_english: bool = False

# 创建提示词管理API
def create_prompt_api(prompt_manager):
    router = APIRouter()
    
    @router.get("/prompts")
    async def get_prompts(category: Optional[str] = None, tag: Optional[str] = None, search: Optional[str] = None):
        """获取提示词列表，支持按分类、标签和搜索查询"""
        try:
            if category:
                # 按分类过滤
                return prompt_manager.get_prompts_by_category(category)
            elif tag:
                # 按标签过滤
                return prompt_manager.get_prompts_by_tag(tag)
            elif search:
                # 搜索过滤
                return prompt_manager.search_prompts(search)
            else:
                # 返回所有提示词
                return prompt_manager.get_all_prompts()
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"获取提示词失败: {str(e)}"}
            )
    
    @router.post("/prompts")
    async def create_prompt(prompt: PromptCreate):
        """创建新提示词"""
        try:
            prompt_id = prompt_manager.add_prompt(
                prompt.title,
                prompt.content,
                prompt.category,
                prompt.tags,
                prompt.auto_translate
            )
            
            # 返回新创建的提示词
            return prompt_manager.get_prompt(prompt_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"创建提示词失败: {str(e)}")
    
    @router.get("/prompts/{prompt_id}")
    async def get_prompt(prompt_id: str):
        """获取单个提示词详情"""
        prompt = prompt_manager.get_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="提示词不存在")
        return prompt
    
    @router.put("/prompts/{prompt_id}")
    async def update_prompt(prompt_id: str, prompt_update: PromptUpdate):
        """更新提示词"""
        success = prompt_manager.update_prompt(
            prompt_id,
            prompt_update.title,
            prompt_update.content,
            prompt_update.category,
            prompt_update.tags,
            prompt_update.auto_translate
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="提示词不存在")
            
        return prompt_manager.get_prompt(prompt_id)
    
    @router.delete("/prompts/{prompt_id}")
    async def delete_prompt(prompt_id: str):
        """删除提示词"""
        success = prompt_manager.delete_prompt(prompt_id)
        if not success:
            raise HTTPException(status_code=404, detail="提示词不存在")
        return {"status": "success", "message": "提示词已删除"}
    
    @router.get("/prompts/categories")
    async def get_categories():
        """获取所有提示词分类"""
        return {"categories": prompt_manager.get_categories()}
    
    @router.post("/prompts/{prompt_id}/translate")
    async def translate_prompt(prompt_id: str, force: bool = Query(False)):
        """翻译指定提示词"""
        try:
            success = prompt_manager.translate_prompt(prompt_id, force)
            if not success:
                raise HTTPException(status_code=404, detail="提示词不存在或翻译失败")
            return prompt_manager.get_prompt(prompt_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")
    
    @router.post("/prompts/{prompt_id}/favorite")
    async def toggle_favorite(prompt_id: str):
        """切换提示词收藏状态"""
        favorite = prompt_manager.toggle_favorite(prompt_id)
        if favorite is None:
            raise HTTPException(status_code=404, detail="提示词不存在")
        return {"id": prompt_id, "favorite": favorite}
    
    @router.post("/translate")
    async def translate_text(request: TranslateRequest):
        """翻译文本"""
        if not request.text or not request.text.strip():
            return JSONResponse(
                status_code=400,
                content={"detail": "文本不能为空"}
            )
            
        try:
            result = prompt_manager.translator.translate_text(
                request.text, 
                to_english=request.to_english
            )
            return {"original": request.text, "translated": result}
        except Exception as e:
            error_msg = str(e)
            print(f"翻译错误: {error_msg}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"翻译失败: {error_msg}"}
            )
    
    @router.post("/batch-translate")
    async def batch_translate(texts: List[str], to_english: bool = Query(False)):
        """批量翻译文本"""
        if not texts:
            return JSONResponse(
                status_code=400,
                content={"detail": "文本列表不能为空"}
            )
            
        try:
            results = prompt_manager.translator.batch_translate(texts, to_english)
            return {"results": [
                {"original": original, "translated": translated}
                for original, translated in zip(texts, results)
            ]}
        except Exception as e:
            error_msg = str(e)
            print(f"批量翻译错误: {error_msg}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"批量翻译失败: {error_msg}"}
            )
    
    return router 