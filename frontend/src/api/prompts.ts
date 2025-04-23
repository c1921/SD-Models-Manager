import axios from 'axios';

// 使用与模型相同的API客户端配置
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 提示词接口定义
export interface Prompt {
  id: string;
  title: string;
  content: string;  // 英文内容
  content_zh: string; // 中文内容
  category: string;
  tags: string[];
  favorite: boolean;
  created_at: number;
  updated_at: number;
  variables: PromptVariable[];
}

// 提示词变量接口
export interface PromptVariable {
  name: string;
  description: string;
  defaultValue: string;
}

// 创建提示词请求参数
export interface CreatePromptParams {
  title: string;
  content: string;
  category: string;
  tags?: string[];
  auto_translate?: boolean;
}

// 更新提示词请求参数
export interface UpdatePromptParams {
  title?: string;
  content?: string;
  category?: string;
  tags?: string[];
  auto_translate?: boolean;
}

// 翻译请求参数
export interface TranslateParams {
  text: string;
  to_english: boolean;
}

// 翻译结果
export interface TranslationResult {
  original: string;
  translated: string;
}

// 提示词API服务
export const PromptsAPI = {
  // 获取所有提示词
  getPrompts: async (category?: string, tag?: string, search?: string): Promise<Prompt[]> => {
    const params: any = {};
    if (category) params.category = category;
    if (tag) params.tag = tag;
    if (search) params.search = search;
    
    const response = await apiClient.get('/prompts', { params });
    return response.data;
  },
  
  // 创建新提示词
  createPrompt: async (params: CreatePromptParams): Promise<Prompt> => {
    const response = await apiClient.post('/prompts', params);
    return response.data;
  },
  
  // 获取单个提示词
  getPrompt: async (id: string): Promise<Prompt> => {
    const response = await apiClient.get(`/prompts/${id}`);
    return response.data;
  },
  
  // 更新提示词
  updatePrompt: async (id: string, params: UpdatePromptParams): Promise<Prompt> => {
    const response = await apiClient.put(`/prompts/${id}`, params);
    return response.data;
  },
  
  // 删除提示词
  deletePrompt: async (id: string): Promise<void> => {
    await apiClient.delete(`/prompts/${id}`);
  },
  
  // 获取所有分类
  getCategories: async (): Promise<string[]> => {
    const response = await apiClient.get('/categories');
    return response.data.categories;
  },
  
  // 翻译提示词
  translatePrompt: async (id: string, force: boolean = false): Promise<Prompt> => {
    const response = await apiClient.post(`/prompts/${id}/translate`, null, {
      params: { force }
    });
    return response.data;
  },
  
  // 切换收藏状态
  toggleFavorite: async (id: string): Promise<boolean> => {
    const response = await apiClient.post(`/prompts/${id}/favorite`);
    return response.data.favorite;
  },
  
  // 翻译文本
  translateText: async (text: string, toEnglish: boolean = false): Promise<TranslationResult> => {
    const response = await apiClient.post('/translate', {
      text,
      to_english: toEnglish
    });
    return response.data;
  },
  
  // 批量翻译
  batchTranslate: async (texts: string[], toEnglish: boolean = false): Promise<TranslationResult[]> => {
    const response = await apiClient.post('/batch-translate', texts, {
      params: { to_english: toEnglish }
    });
    return response.data.results;
  }
}; 