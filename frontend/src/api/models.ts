import axios from 'axios';

// 设置基础URL，与后端接口对应
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 模型接口定义
export interface Model {
  id: string;
  name: string;
  filename: string;
  type: string;
  size?: number;
  preview?: string;
  nsfw?: boolean;
  created_at?: string;
  hash?: string;
  tags?: string[];
  base_model?: string;
  url?: string;
}

// 后端返回的模型数据格式
interface BackendModel {
  path: string;
  name: string;
  type: string;
  preview_url?: string;
  nsfw?: boolean;
  baseModel?: string;
  url?: string;
  nsfwLevel?: number;
}

// 转换后端模型格式为前端格式
function convertModel(backendModel: BackendModel): Model {
  // 提取文件名
  const filename = backendModel.path.split(/[/\\]/).pop() || '';
  
  return {
    id: backendModel.path, // 使用路径作为唯一ID
    name: backendModel.name,
    filename: filename,
    type: backendModel.type,
    preview: backendModel.preview_url,
    nsfw: backendModel.nsfw || false,
    base_model: backendModel.baseModel,
    url: backendModel.url
  };
}

// API服务
export const ModelsAPI = {
  // 获取模型目录
  getModelPath: async (): Promise<string> => {
    const response = await apiClient.get('/config');
    return response.data.models_path;
  },

  // 设置模型目录
  setModelPath: async (path: string): Promise<void> => {
    await apiClient.post('/path', { path });
  },

  // 选择模型目录（通过系统对话框）
  selectModelPath: async (): Promise<string> => {
    try {
      const response = await apiClient.get('/select-path');
      if (response.data.updated) {
        // 如果后端已经更新了路径，不需要再次调用setModelPath
        return response.data.path;
      } else if (response.data.path) {
        // 如果有路径但未更新，手动更新
        await ModelsAPI.setModelPath(response.data.path);
        return response.data.path;
      }
      // 如果没有路径，返回空字符串
      return '';
    } catch (e) {
      console.error('选择目录失败', e);
      throw e;
    }
  },

  // 获取所有模型
  getModels: async (): Promise<Model[]> => {
    const response = await apiClient.get('/models');
    // 转换响应数据格式
    return (response.data as BackendModel[]).map(convertModel);
  },

  // 扫描模型
  scanModels: async (): Promise<{ taskId: string }> => {
    // 关闭之前可能存在的EventSource连接
    const previousScan = (window as any).modelScanEventSource;
    if (previousScan?.eventSource) {
      previousScan.eventSource.close();
    }
    
    // 开始SSE扫描连接
    const eventSource = new EventSource('/api/scan');
    const taskId = Date.now().toString(); // 生成唯一任务ID
    
    // 初始化任务状态
    (window as any).modelScanEventSource = {
      eventSource,
      taskId,
      listeners: {},
      completed: false,
      progress: 0,
      message: '开始扫描...'
    };
    
    // 立即添加事件监听器
    eventSource.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        console.log('收到扫描事件:', data); // 调试日志
        
        // 更新全局状态
        const scanState = (window as any).modelScanEventSource;
        scanState.progress = data.progress || 0;
        scanState.message = data.message || '';
        
        if (data.status === 'completed') {
          console.log('扫描完成，进度:', scanState.progress); // 调试日志
          scanState.completed = true;
          eventSource.close();
        }
      } catch (e) {
        console.error('解析事件数据出错', e);
      }
    };
    
    eventSource.onerror = (error) => {
      console.error('扫描事件源错误:', error); // 调试日志
      const scanState = (window as any).modelScanEventSource;
      scanState.completed = true;
      scanState.message = '扫描过程中出现错误';
      eventSource.close();
    };
    
    return { taskId };
  },

  // 获取扫描状态
  getScanStatus: async (_taskId: string): Promise<{ progress: number; message: string; completed: boolean }> => {
    // 从全局获取事件源状态
    const scanState = (window as any).modelScanEventSource;
    
    if (!scanState) {
      return { progress: 0, message: '未找到扫描任务', completed: true };
    }
    
    // 进行深拷贝避免引用问题
    return {
      progress: Number(scanState.progress) || 0,
      message: scanState.message || '',
      completed: Boolean(scanState.completed)
    };
  },

  // 获取模型详情
  getModelDetails: async (modelId: string): Promise<Model> => {
    // 在实际情况下，这里可能需要一个专门的API端点
    // 目前我们只返回原始模型信息
    const response = await apiClient.get('/models');
    const models = response.data as BackendModel[];
    const model = models.find(m => m.path === modelId);
    
    if (!model) {
      throw new Error('模型不存在');
    }
    
    return convertModel(model);
  },
  
  // 获取应用版本信息
  getVersion: async (): Promise<{version: string; company: string; copyright: string}> => {
    const response = await apiClient.get('/version');
    return response.data;
  }
}; 