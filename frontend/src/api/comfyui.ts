import axios from 'axios';

// 设置基础URL，与后端接口对应
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// ComfyUI API服务
export const ComfyUIAPI = {
  // 检查ComfyUI状态
  checkStatus: async (): Promise<{status: 'running' | 'stopped' | 'unknown', message: string}> => {
    const response = await apiClient.get('/comfyui-status');
    return response.data;
  }
}; 