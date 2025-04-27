import axios from 'axios';

// 设置基础URL，与后端接口对应
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 网络连接状态结果接口
export interface NetworkStatusResult {
  available: boolean;
  status_code: number | null;
  response_time: number;
  message: string;
}

// 网络目标状态接口
export interface NetworkTargetStatus {
  name: string;
  url: string;
  result: NetworkStatusResult;
}

// 完整网络状态响应接口
export interface NetworkStatusResponse {
  status: 'fresh' | 'cached';
  last_check: number;
  results: {
    [key: string]: NetworkTargetStatus;
  };
}

// 网络API服务
export const NetworkAPI = {
  /**
   * 检查网络连接状态
   * 
   * @param forceRefresh 是否强制刷新状态（不使用缓存）
   * @returns 网络连接状态信息
   */
  checkStatus: async (forceRefresh: boolean = false): Promise<NetworkStatusResponse> => {
    const response = await apiClient.get('/network-status', {
      params: { force_refresh: forceRefresh }
    });
    return response.data;
  },

  /**
   * 检查Civitai API连接状态
   * 
   * @param forceRefresh 是否强制刷新状态
   * @returns Civitai状态信息
   */
  checkCivitaiStatus: async (forceRefresh: boolean = false): Promise<NetworkTargetStatus> => {
    const response = await NetworkAPI.checkStatus(forceRefresh);
    return response.results.civitai;
  },

  /**
   * 检查Google翻译连接状态
   * 
   * @param forceRefresh 是否强制刷新状态
   * @returns Google翻译状态信息
   */
  checkGoogleTranslateStatus: async (forceRefresh: boolean = false): Promise<NetworkTargetStatus> => {
    const response = await NetworkAPI.checkStatus(forceRefresh);
    return response.results.google_translate;
  }
}; 