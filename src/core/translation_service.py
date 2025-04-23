from deep_translator import GoogleTranslator
from typing import List, Tuple, Optional
import time
import asyncio

class TranslationService:
    def __init__(self, max_retries=3, retry_delay=1):
        self.max_retries = max_retries  # 最大重试次数
        self.retry_delay = retry_delay  # 重试延迟（秒）
        self.init_translators()
        
    def init_translators(self):
        """初始化翻译器，便于重新创建实例"""
        try:
            self.en_to_zh = GoogleTranslator(source='en', target='zh-CN')
            self.zh_to_en = GoogleTranslator(source='zh-CN', target='en')
            return True
        except Exception as e:
            print(f"初始化翻译器失败: {str(e)}")
            return False
    
    def translate_text(self, text: str, to_english: bool = False) -> str:
        """翻译单个文本，支持重试"""
        if not text or len(text.strip()) == 0:
            return ""
            
        for attempt in range(self.max_retries):
            try:
                translator = self.zh_to_en if to_english else self.en_to_zh
                return translator.translate(text)
            except Exception as e:
                # 最后一次尝试失败，抛出异常
                if attempt == self.max_retries - 1:
                    raise TranslationError(f"翻译失败 (尝试 {attempt+1}/{self.max_retries}): {str(e)}")
                
                print(f"翻译尝试 {attempt+1}/{self.max_retries} 失败: {str(e)}, 将在 {self.retry_delay}秒后重试")
                time.sleep(self.retry_delay)
                
                # 尝试重新初始化翻译器
                if attempt == 0:  # 只在第一次失败后尝试重新初始化
                    self.init_translators()
    
    def batch_translate(self, texts: List[str], to_english: bool = False) -> List[str]:
        """批量翻译文本，支持重试"""
        if not texts:
            return []
            
        # 过滤空文本
        filtered_texts = [t for t in texts if t and len(t.strip()) > 0]
        if not filtered_texts:
            return [""] * len(texts)
            
        for attempt in range(self.max_retries):
            try:
                translator = self.zh_to_en if to_english else self.en_to_zh
                # 分批处理，每批最多5个文本
                batch_size = 5
                results = []
                
                for i in range(0, len(filtered_texts), batch_size):
                    batch = filtered_texts[i:i+batch_size]
                    combined = "\n".join(batch)
                    translated = translator.translate(combined)
                    
                    # 检查返回结果是否为有效值
                    if not translated:
                        raise TranslationError("翻译服务返回空结果")
                        
                    batch_results = [r.strip() for r in translated.split("\n")]
                    
                    # 确保返回结果数量与输入相同
                    if len(batch_results) != len(batch):
                        print(f"警告: 翻译返回的条目数 ({len(batch_results)}) 与请求的条目数 ({len(batch)}) 不一致")
                        # 尝试填充或截断结果以匹配输入数量
                        if len(batch_results) < len(batch):
                            batch_results.extend([''] * (len(batch) - len(batch_results)))
                        else:
                            batch_results = batch_results[:len(batch)]
                            
                    results.extend(batch_results)
                    
                    # 添加短暂延迟，避免API限制
                    if i + batch_size < len(filtered_texts):
                        time.sleep(0.5)
                
                # 恢复原始顺序和空文本占位
                final_results = []
                result_index = 0
                for text in texts:
                    if text and len(text.strip()) > 0:
                        if result_index < len(results):
                            final_results.append(results[result_index])
                            result_index += 1
                        else:
                            final_results.append("")  # 安全处理：如果结果不足
                    else:
                        final_results.append("")
                
                return final_results
                
            except Exception as e:
                # 最后一次尝试失败，抛出异常
                if attempt == self.max_retries - 1:
                    raise TranslationError(f"批量翻译失败 (尝试 {attempt+1}/{self.max_retries}): {str(e)}")
                
                print(f"批量翻译尝试 {attempt+1}/{self.max_retries} 失败: {str(e)}, 将在 {self.retry_delay}秒后重试")
                time.sleep(self.retry_delay)
                
                # 尝试重新初始化翻译器
                if attempt == 0:  # 只在第一次失败后尝试重新初始化
                    self.init_translators()


class TranslationError(Exception):
    """翻译错误异常类"""
    pass 