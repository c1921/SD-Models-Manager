from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

class TranslateRequest(BaseModel):
    text: str
    to_english: bool = False

# 创建翻译API
def create_prompt_api(prompt_manager):
    router = APIRouter()
    
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
    async def batch_translate(texts: List[str], to_english: bool = False):
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