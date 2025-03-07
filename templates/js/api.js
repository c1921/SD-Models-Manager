const API_BASE = `http://localhost:${window.location.port}/api`;

// API 请求相关函数
const api = {
    // 加载配置
    async loadConfig() {
        const response = await fetch(`${API_BASE}/config`);
        if (!response.ok) throw new Error('加载配置失败');
        return await response.json();
    },

    // 选择目录
    async selectDirectory() {
        const response = await fetch(`${API_BASE}/select_directory`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('选择目录失败');
        return await response.json();
    },

    // 保存选择的路径
    async saveSelectedPath(path) {
        const response = await fetch(`${API_BASE}/path`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: path }),
        });
        if (!response.ok) throw new Error('路径无效');
        return await response.json();
    },

    // 加载模型列表
    async loadModels() {
        const response = await fetch(`${API_BASE}/models`);
        if (!response.ok) throw new Error('加载模型列表失败');
        return await response.json();
    },

    // 创建扫描事件源
    createScanEventSource() {
        return new EventSource(`${API_BASE}/scan`);
    }
};

export default api; 