import api from './api.js';
import filterManager from './filters.js';
import modelManager from './models.js';
import ui from './ui.js';
const pathInput = document.getElementById('pathInput');
const selectPathBtn = document.getElementById('selectPath');
const scanModelsBtn = document.getElementById('scanModels');
const filterContainer = document.getElementById('filterContainer');
const filterContainerMobile = document.getElementById('filterContainerMobile');

// 存储所有模型数据
let allModels = [];

// 加载配置
async function loadConfig() {
    try {
        const config = await api.loadConfig();
        if (config.models_path) {
            pathInput.value = config.models_path;
        }
    } catch (err) {
        ui.showError('加载配置失败');
    }
}

// 选择目录
selectPathBtn.addEventListener('click', async () => {
    try {
        const data = await api.selectDirectory();
        if (data.path) {
            pathInput.value = data.path;
            await saveSelectedPath(data.path);
        }
    } catch (err) {
        ui.showError('选择目录失败');
    }
});

// 选择并保存路径
async function saveSelectedPath(path) {
    try {
        await api.saveSelectedPath(path);
        loadModels();
    } catch (err) {
        ui.showError(err.message);
    }
}

// 扫描模型
scanModelsBtn.addEventListener('click', async () => {
    try {
        scanModelsBtn.disabled = true;
        ui.showLoading();

        const eventSource = api.createScanEventSource();

        eventSource.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            ui.updateProgress(data.progress, data.message);

            // 实时更新模型列表
            if (data.message.startsWith('已处理:')) {
                await loadModels();
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            scanModelsBtn.disabled = false;
            ui.hideLoading();
        };
    } catch (err) {
        ui.showError(err.message);
        scanModelsBtn.disabled = false;
        ui.hideLoading();
    }
});

// 加载模型列表
async function loadModels() {
    try {
        allModels = await api.loadModels();

        // 更新筛选器选项
        filterManager.updateFilterOptions(allModels, filterContainer, filterContainerMobile);

        // 显示模型
        const filteredModels = filterManager.applyFilters(allModels, ui.getNSFWState());
        modelManager.displayModels(filteredModels);
    } catch (err) {
        ui.showError('加载模型列表失败');
    }
}

// 监听筛选器更新事件
document.addEventListener('filtersUpdated', () => {
    const filteredModels = filterManager.applyFilters(allModels, ui.getNSFWState());
    modelManager.displayModels(filteredModels);
});

// 监听 NSFW 状态变化
document.addEventListener('nsfwStateChanged', (e) => {
    const filteredModels = filterManager.applyFilters(allModels, e.detail);
    modelManager.displayModels(filteredModels);
});

// 页面加载时初始化
loadConfig();
loadModels();
