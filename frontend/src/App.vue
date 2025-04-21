<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 使用导航栏组件 -->
    <AppNavbar
      :nsfw="nsfw"
      :dark-mode="darkMode"
      @toggle-nsfw="toggleNsfw"
      @toggle-dark-mode="toggleDarkMode"
      @open-settings="openSettings"
      @open-filter-sidebar="openFilterSidebar"
    />

    <!-- 设置模态窗组件 -->
    <SettingsModal
      ref="settingsModalRef"
      :app-version="appVersion"
      :model-path="modelPath"
      @update:model-path="modelPath = $event"
      @scan-models="scanModelsAndClose"
    />

    <!-- 模型详情模态框组件 -->
    <ModelDetailModal
      ref="modelDetailModalRef"
      :model="selectedModel"
      @close="closeModelDetail"
    />

    <div class="container mx-auto px-4 py-6">
      <div class="flex flex-col lg:flex-row">
        <!-- 主内容区 - 模型列表组件 -->
        <div class="flex-1">
          <ModelList
            :models="models"
            :filtered-models="filteredModels"
            :loading="loading"
            :progress="progress"
            :progress-message="progressMessage"
            :error="error"
            :nsfw="nsfw"
            @model-click="openModelDetails"
            @open-settings="openSettings"
          />
        </div>

        <!-- 筛选器侧边栏组件 -->
        <FilterSidebar 
          ref="filterSidebarRef"
          :filters="filters"
          :model-count="models.length"
        />
      </div>
    </div>

    <!-- 提示消息容器 -->
    <div id="notification-container" class="notification-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch, onUnmounted } from 'vue';
import { ModelsAPI } from './api/models';
import type { Model } from './api/models';
import FilterSidebar from './components/FilterSidebar.vue';
import ModelList from './components/ModelList.vue';
import ModelDetailModal from './components/ModelDetailModal.vue';
import AppNavbar from './components/AppNavbar.vue';
import SettingsModal from './components/SettingsModal.vue';

// 类型定义
interface FilterOption {
  label: string;
  value: string;
  count: number;
}

interface Filter {
  label: string;
  options: FilterOption[];
  selected: string[];
}

// 状态管理
const appVersion = ref('');
const modelPath = ref('');
const models = ref<Model[]>([]);
const nsfw = ref(false);
const darkMode = ref(false);
const loading = ref(false);
const progress = ref(0);
const progressMessage = ref('');
const error = ref('');
const selectedModel = ref<Model | null>(null);
let scanInterval: number | null = null;
let currentScanTaskId: string | null = null;

// UI状态控制
const filterSidebarRef = ref<InstanceType<typeof FilterSidebar> | null>(null);
const modelDetailModalRef = ref<InstanceType<typeof ModelDetailModal> | null>(null);
const settingsModalRef = ref<InstanceType<typeof SettingsModal> | null>(null);

// 筛选器状态
const filters = reactive<Record<string, Filter>>({
  type: {
    label: '模型类型',
    options: [],
    selected: []
  },
  base_model: {
    label: '基础模型',
    options: [],
    selected: []
  }
});

// 计算过滤后的模型列表
const filteredModels = computed(() => {
  let result = models.value;
  
  // 应用 NSFW 过滤
  if (!nsfw.value) {
    result = result.filter(model => !model.nsfw);
  }
  
  // 应用其他筛选器
  Object.keys(filters).forEach(key => {
    const filter = filters[key];
    if (filter.selected.length > 0) {
      result = result.filter(model => {
        // @ts-ignore - 动态访问模型属性
        const value = model[key];
        return value && filter.selected.includes(value);
      });
    }
  });
  
  return result;
});

// 更新筛选器选项
function updateFilterOptions() {
  // 模型类型筛选器
  const typeMap = new Map<string, number>();
  const baseModelMap = new Map<string, number>();
  
  models.value.forEach(model => {
    // 更新类型计数
    if (model.type) {
      const count = typeMap.get(model.type) || 0;
      typeMap.set(model.type, count + 1);
    }
    
    // 更新基础模型计数
    if (model.base_model) {
      const count = baseModelMap.get(model.base_model) || 0;
      baseModelMap.set(model.base_model, count + 1);
    }
  });
  
  // 更新类型筛选器选项
  filters.type.options = Array.from(typeMap.entries()).map(([value, count]) => ({
    label: value,
    value,
    count
  })).sort((a, b) => b.count - a.count);
  
  // 更新基础模型筛选器选项
  filters.base_model.options = Array.from(baseModelMap.entries()).map(([value, count]) => ({
    label: value,
    value,
    count
  })).sort((a, b) => b.count - a.count);
}

// 方法
function toggleNsfw() {
  nsfw.value = !nsfw.value;
  // 保存设置到 localStorage
  localStorage.setItem('nsfw', String(nsfw.value));
}

function toggleDarkMode() {
  darkMode.value = !darkMode.value;
  document.documentElement.classList.toggle('dark', darkMode.value);
  // 保存设置到 localStorage
  localStorage.setItem('darkMode', String(darkMode.value));
}

function openSettings() {
  if (settingsModalRef.value) {
    settingsModalRef.value.open();
  }
}

function openFilterSidebar() {
  if (filterSidebarRef.value) {
    filterSidebarRef.value.openFilterSidebar();
  }
}

function scanModelsAndClose() {
  scanModels();
}

async function scanModels() {
  try {
    loading.value = true;
    progress.value = 0;
    progressMessage.value = '正在扫描模型...';
    error.value = '';
    
    // 开始扫描
    const { taskId } = await ModelsAPI.scanModels();
    currentScanTaskId = taskId;
    
    // 轮询状态
    if (scanInterval) {
      clearInterval(scanInterval);
    }
    
    scanInterval = window.setInterval(async () => {
      if (!currentScanTaskId) return;
      
      try {
        const status = await ModelsAPI.getScanStatus(currentScanTaskId);
        progress.value = status.progress;
        progressMessage.value = status.message;
        
        if (status.completed) {
          clearInterval(scanInterval as number);
          scanInterval = null;
          currentScanTaskId = null;
          
          // 重新获取模型列表
          await loadModels();
          
          // 显示完成提示
          showCompletionNotification();
        }
      } catch (e) {
        console.error('获取扫描状态失败', e);
        clearInterval(scanInterval as number);
        scanInterval = null;
        currentScanTaskId = null;
        error.value = '获取扫描状态失败';
        loading.value = false;
      }
    }, 1000);
  } catch (e) {
    console.error('扫描模型失败', e);
    error.value = '扫描模型失败';
    loading.value = false;
  }
}

async function loadModels() {
  try {
    // 获取模型列表
    models.value = await ModelsAPI.getModels();
    
    // 更新筛选器选项
    updateFilterOptions();
    
    loading.value = false;
  } catch (e) {
    console.error('加载模型列表失败', e);
    error.value = '加载模型列表失败';
    loading.value = false;
  }
}

async function loadModelPath() {
  try {
    modelPath.value = await ModelsAPI.getModelPath();
  } catch (e) {
    console.error('获取模型目录失败', e);
  }
}

function openModelDetails(model: Model) {
  selectedModel.value = model;
  // 打开模型详情模态框
  if (modelDetailModalRef.value) {
    modelDetailModalRef.value.open();
  }
}

function closeModelDetail() {
  selectedModel.value = null;
}

// 监听模型列表变化
watch(models, () => {
  updateFilterOptions();
}, { deep: true });

// 生命周期钩子
onMounted(async () => {
  // 从 localStorage 加载设置
  const savedNsfw = localStorage.getItem('nsfw');
  if (savedNsfw !== null) {
    nsfw.value = savedNsfw === 'true';
  }
  
  const savedDarkMode = localStorage.getItem('darkMode');
  if (savedDarkMode !== null) {
    darkMode.value = savedDarkMode === 'true';
  } else {
    // 检查系统主题偏好
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      darkMode.value = true;
    }
  }
  
  // 应用初始主题
  document.documentElement.classList.toggle('dark', darkMode.value);
  
  // 获取应用版本
  try {
    const versionInfo = await ModelsAPI.getVersion();
    appVersion.value = versionInfo.version;
  } catch (e) {
    console.error('获取版本信息失败', e);
    appVersion.value = '0.2.0'; // 默认版本号
  }
  
  // 加载模型目录
  await loadModelPath();
  
  // 加载模型列表
  loading.value = true;
  await loadModels();
});

// 组件卸载时清理
onUnmounted(() => {
  if (scanInterval) {
    clearInterval(scanInterval);
    scanInterval = null;
  }
});

// 显示扫描完成通知
function showCompletionNotification() {
  // 使用FlyonUI的toast API
  const notificationContainer = document.getElementById('notification-container');
  if (notificationContainer) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = 'notification notification-success';
    notification.innerHTML = `
      <div class="notification-icon">
        <span class="icon-[tabler--check] size-5"></span>
      </div>
      <div class="notification-content">
        <div class="notification-title">扫描完成</div>
        <div class="notification-message">所有模型已扫描完成</div>
      </div>
    `;
    notificationContainer.appendChild(notification);
    
    // 3秒后移除通知
    setTimeout(() => {
      notification.classList.add('notification-hide');
      setTimeout(() => {
        notificationContainer.removeChild(notification);
      }, 300);
    }, 3000);
  }
}
</script>