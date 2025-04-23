import json
import time
import uuid
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.core.translation_service import TranslationService, TranslationError

class PromptManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.prompts_file = self.config.get("prompts_file", "prompts_data.json")
        self.prompts = {}
        self.categories = set()
        self.translator = TranslationService()
        # 加载已有的提示词
        self.load_prompts()
        
    def load_config(self) -> dict:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 添加提示词相关配置
                if "prompts_file" not in config:
                    config["prompts_file"] = "prompts_data.json"
                return config
        return {"models_path": "", "output_file": "models_info.json", "prompts_file": "prompts_data.json"}
    
    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
    def load_prompts(self):
        """从JSON文件加载提示词数据"""
        if os.path.exists(self.prompts_file):
            with open(self.prompts_file, "r", encoding="utf-8") as f:
                try:
                    self.prompts = json.load(f)
                    # 更新分类集合
                    self.categories = set(prompt.get("category", "") 
                                         for prompt in self.prompts.values() 
                                         if prompt.get("category"))
                except json.JSONDecodeError:
                    # 文件损坏，创建新的
                    self.prompts = {}
                    self.categories = set()
        else:
            # 文件不存在，初始化为空
            self.prompts = {}
            self.categories = set()
    
    def save_prompts(self):
        """保存提示词到JSON文件"""
        with open(self.prompts_file, "w", encoding="utf-8") as f:
            json.dump(self.prompts, f, ensure_ascii=False, indent=2)
    
    def add_prompt(self, title: str, content: str, category: str, 
                  tags: List[str] = None, auto_translate: bool = True) -> str:
        """添加新提示词，可选自动翻译"""
        prompt_id = str(uuid.uuid4())
        
        # 检测输入的内容是中文还是英文
        is_chinese = self._is_chinese_text(content)
        
        # 初始化提示词对象
        prompt = {
            "id": prompt_id,
            "title": title,
            "content": content if not is_chinese else "",
            "content_zh": content if is_chinese else "",
            "category": category,
            "tags": tags or [],
            "favorite": False,
            "created_at": time.time(),
            "updated_at": time.time(),
            "variables": []
        }
        
        # 自动翻译
        if auto_translate and content.strip():
            try:
                if is_chinese:
                    # 中文内容，翻译成英文
                    prompt["content"] = self.translator.translate_text(content, to_english=True)
                else:
                    # 英文内容，翻译成中文
                    prompt["content_zh"] = self.translator.translate_text(content)
            except TranslationError as e:
                print(f"翻译失败: {str(e)}")
        
        # 保存提示词
        self.prompts[prompt_id] = prompt
        if category:
            self.categories.add(category)
        self.save_prompts()
        return prompt_id
    
    def update_prompt(self, prompt_id: str, title: Optional[str] = None, 
                     content: Optional[str] = None, category: Optional[str] = None,
                     tags: Optional[List[str]] = None, auto_translate: bool = True) -> bool:
        """更新提示词信息"""
        if prompt_id not in self.prompts:
            return False
        
        prompt = self.prompts[prompt_id]
        
        # 更新字段
        if title is not None:
            prompt["title"] = title
        
        if content is not None:
            # 检测输入内容是中文还是英文
            is_chinese = self._is_chinese_text(content)
            
            if is_chinese:
                prompt["content_zh"] = content
                # 自动翻译成英文
                if auto_translate:
                    try:
                        prompt["content"] = self.translator.translate_text(content, to_english=True)
                    except TranslationError as e:
                        print(f"翻译失败: {str(e)}")
            else:
                prompt["content"] = content
                # 自动翻译成中文
                if auto_translate:
                    try:
                        prompt["content_zh"] = self.translator.translate_text(content)
                    except TranslationError as e:
                        print(f"翻译失败: {str(e)}")
        
        if category is not None:
            prompt["category"] = category
            if category:
                self.categories.add(category)
        
        if tags is not None:
            prompt["tags"] = tags
        
        # 更新时间戳
        prompt["updated_at"] = time.time()
        
        # 保存更改
        self.save_prompts()
        return True
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """删除提示词"""
        if prompt_id not in self.prompts:
            return False
        
        del self.prompts[prompt_id]
        
        # 更新分类集合
        self.categories = set(prompt.get("category", "") 
                             for prompt in self.prompts.values() 
                             if prompt.get("category"))
        
        # 保存更改
        self.save_prompts()
        return True
    
    def get_prompt(self, prompt_id: str) -> Optional[dict]:
        """获取单个提示词信息"""
        return self.prompts.get(prompt_id)
    
    def get_all_prompts(self) -> List[dict]:
        """获取所有提示词信息"""
        return [
            {**prompt, "id": id}
            for id, prompt in self.prompts.items()
        ]
    
    def get_prompts_by_category(self, category: str) -> List[dict]:
        """按分类获取提示词"""
        return [
            {**prompt, "id": id}
            for id, prompt in self.prompts.items()
            if prompt.get("category") == category
        ]
    
    def get_prompts_by_tag(self, tag: str) -> List[dict]:
        """按标签获取提示词"""
        return [
            {**prompt, "id": id}
            for id, prompt in self.prompts.items()
            if tag in prompt.get("tags", [])
        ]
    
    def search_prompts(self, query: str) -> List[dict]:
        """搜索提示词"""
        query = query.lower()
        results = []
        
        for id, prompt in self.prompts.items():
            # 在标题和内容中搜索
            if (query in prompt.get("title", "").lower() or
                query in prompt.get("content", "").lower() or
                query in prompt.get("content_zh", "").lower() or
                any(query in tag.lower() for tag in prompt.get("tags", []))):
                results.append({**prompt, "id": id})
        
        return results
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return sorted(list(self.categories))
    
    def translate_prompt(self, prompt_id: str, force: bool = False) -> bool:
        """翻译指定提示词
        
        Args:
            prompt_id: 提示词ID
            force: 是否强制重新翻译，即使已有翻译
            
        Returns:
            bool: 翻译是否成功
        """
        if prompt_id not in self.prompts:
            return False
        
        prompt = self.prompts[prompt_id]
        try:
            # 根据内容判断翻译方向
            if prompt.get("content") and (not prompt.get("content_zh") or force):
                # 英文到中文
                prompt["content_zh"] = self.translator.translate_text(prompt["content"])
                success = True
            elif prompt.get("content_zh") and (not prompt.get("content") or force):
                # 中文到英文
                prompt["content"] = self.translator.translate_text(prompt["content_zh"], to_english=True)
                success = True
            else:
                # 没有内容可翻译
                success = False
            
            if success:
                prompt["updated_at"] = time.time()
                self.save_prompts()
            
            return success
        except TranslationError as e:
            print(f"翻译失败: {str(e)}")
            return False
    
    def toggle_favorite(self, prompt_id: str) -> bool:
        """切换提示词收藏状态"""
        if prompt_id not in self.prompts:
            return False
        
        self.prompts[prompt_id]["favorite"] = not self.prompts[prompt_id].get("favorite", False)
        self.save_prompts()
        return self.prompts[prompt_id]["favorite"]
    
    def _is_chinese_text(self, text: str) -> bool:
        """判断文本是否主要为中文"""
        if not text:
            return False
            
        # 简单判断：如果中文字符数量超过总字符的30%，则认为是中文
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        return chinese_chars / len(text) > 0.3 