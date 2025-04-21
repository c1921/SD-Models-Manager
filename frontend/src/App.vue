<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 导航栏 -->
    <nav class="sticky top-0 z-10 bg-white dark:bg-gray-800 shadow">
      <div class="container mx-auto px-4 flex items-center justify-between h-16">
        <a href="#" class="flex items-center">
          <img src="/favicon.svg" alt="Stable Diffusion 模型管理器" class="h-7">
        </a>
        
        <div class="flex items-center space-x-3">
          <button 
            type="button"
            class="btn" 
            :class="nsfw ? 'btn-primary' : 'btn-outline-primary'"
            @click="toggleNsfw"
          >
            <span 
              class="inline-block me-1.5 size-4"
              :class="nsfw ? 'icon-[tabler--eye]' : 'icon-[tabler--eye-off]'"
            ></span>
            <span>NSFW {{ nsfw ? '已开启' : '已关闭' }}</span>
          </button>

          <button 
            type="button"
            class="btn btn-icon btn-ghost"
            @click="openSettings"
          >
            <span class="icon-[tabler--settings] size-5"></span>
          </button>

          <button 
            type="button"
            class="btn btn-icon btn-ghost"
            @click="toggleDarkMode"
          >
            <span 
              class="size-5"
              :class="darkMode ? 'icon-[tabler--moon]' : 'icon-[tabler--sun]'"
            ></span>
          </button>
          
          <button 
            type="button"
            class="btn btn-icon btn-ghost lg:hidden"
            @click="openFilterSidebar"
          >
            <span class="icon-[tabler--filter] size-5"></span>
          </button>
        </div>
      </div>
    </nav>

    <!-- 设置模态窗 -->
    <button 
      ref="settingsModalTrigger" 
      type="button" 
      class="hidden" 
      aria-haspopup="dialog" 
      aria-expanded="false" 
      aria-controls="settings-modal" 
      data-overlay="#settings-modal"
    ></button>

    <div 
      id="settings-modal" 
      class="overlay modal overlay-open:opacity-100 hidden overlay-open:duration-300" 
      role="dialog" 
      tabindex="-1"
    >
      <div class="modal-dialog overlay-open:opacity-100 overlay-open:duration-300">
        <div class="modal-content bg-gray-50 dark:bg-gray-800">
          <div class="modal-header border-b border-gray-200 dark:border-gray-700">
            <h3 class="modal-title">设置</h3>
            <button 
              type="button" 
              class="btn btn-text btn-circle btn-sm absolute end-3 top-3 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300" 
              aria-label="关闭" 
              data-overlay="#settings-modal"
            >
              <span class="icon-[tabler--x] size-4"></span>
            </button>
          </div>
          <div class="modal-body">
            <nav class="tabs tabs-bordered overflow-x-auto" aria-label="设置标签" role="tablist" aria-orientation="horizontal">
              <button 
                type="button" 
                class="tab active-tab:tab-active active" 
                id="path-tab-item" 
                data-tab="#path-tab-content" 
                aria-controls="path-tab-content" 
                role="tab" 
                aria-selected="true"
              >
                <span class="icon-[tabler--folder] size-5 shrink-0 me-2"></span>
                路径设置
              </button>
              <button 
                type="button" 
                class="tab active-tab:tab-active" 
                id="about-tab-item" 
                data-tab="#about-tab-content" 
                aria-controls="about-tab-content" 
                role="tab" 
                aria-selected="false"
              >
                <span class="icon-[tabler--info-circle] size-5 shrink-0 me-2"></span>
                关于
              </button>
            </nav>
            
            <div class="mt-4">
              <div id="path-tab-content" role="tabpanel" aria-labelledby="path-tab-item">
                <div class="mb-6">
                  <label for="modelPath" class="label">
                    <span class="label-text font-medium text-gray-700 dark:text-gray-300">模型目录</span>
                  </label>
                  <div class="flex items-center space-x-2">
                    <input 
                      id="modelPath"
                      type="text" 
                      class="input input-bordered flex-1 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300" 
                      placeholder="请选择模型目录" 
                      readonly 
                      v-model="modelPath"
                    >
                    <button 
                      type="button" 
                      class="btn btn-primary" 
                      @click="selectPath"
                    >
                      <span class="icon-[tabler--folder-open] me-1.5 size-4"></span>
                      浏览
                    </button>
                  </div>
                </div>
              </div>
              
              <div id="about-tab-content" class="hidden" role="tabpanel" aria-labelledby="about-tab-item">
                <div class="flex flex-col items-center py-4">
                  <img src="/favicon.svg" alt="logo" class="h-16 mb-3">
                  <h5 class="text-lg font-medium mb-2 text-gray-800 dark:text-gray-200">SD Models Manager</h5>
                  <p class="text-gray-600 dark:text-gray-400 mb-3">版本 <span>{{ appVersion }}</span></p>
                  <p class="mb-2">
                    <a href="https://github.com/c1921/SD-Models-Manager" target="_blank" class="text-primary hover:text-primary-dark flex items-center">
                      <span class="icon-[tabler--brand-github] inline-block me-1.5 size-5"></span>
                      GitHub
                    </a>
                  </p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">MIT 开源许可 - 版权所有 (c) 2025</p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-t border-gray-200 dark:border-gray-700">
            <button 
              type="button" 
              class="btn btn-soft btn-secondary text-gray-700 dark:text-gray-300" 
              data-overlay="#settings-modal"
            >
              关闭
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="scanModelsAndClose"
              data-overlay="#settings-modal"
            >
              扫描模型
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型详情模态框 -->
    <button 
      ref="modelDetailTrigger" 
      type="button" 
      class="hidden" 
      aria-haspopup="dialog" 
      aria-expanded="false" 
      aria-controls="model-detail-modal" 
      data-overlay="#model-detail-modal"
    ></button>

    <div 
      id="model-detail-modal" 
      class="overlay modal overlay-open:opacity-100 hidden overlay-open:duration-300" 
      role="dialog" 
      tabindex="-1"
    >
      <div class="modal-dialog overlay-open:opacity-100 overlay-open:duration-300 max-w-4xl">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">{{ selectedModel?.name || '' }}</h3>
            <button 
              type="button" 
              class="btn btn-text btn-circle btn-sm absolute end-3 top-3" 
              aria-label="关闭" 
              data-overlay="#model-detail-modal"
              @click="closeModelDetail"
            >
              <span class="icon-[tabler--x] size-4"></span>
            </button>
          </div>
          <div class="modal-body">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="md:col-span-2">
                <img 
                  v-if="selectedModel?.preview" 
                  :src="selectedModel.preview" 
                  class="w-full rounded-lg" 
                  :alt="selectedModel?.name">
                <div 
                  v-else 
                  class="flex flex-col items-center justify-center p-12 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <span class="icon-[tabler--photo] size-12 text-gray-400"></span>
                  <p class="mt-3 text-gray-500">无预览图</p>
                </div>
              </div>
              <div>
                <div v-if="selectedModel" class="flex flex-col space-y-3">
                  <p><span class="font-medium">文件名:</span> {{ selectedModel.filename }}</p>
                  <p><span class="font-medium">模型类型:</span> {{ selectedModel.type }}</p>
                  <p v-if="selectedModel.size"><span class="font-medium">文件大小:</span> {{ formatFileSize(selectedModel.size) }}</p>
                  <p v-if="selectedModel.created_at"><span class="font-medium">创建时间:</span> {{ formatDate(selectedModel.created_at) }}</p>
                  <p v-if="selectedModel.hash"><span class="font-medium">哈希值:</span> {{ selectedModel.hash }}</p>
                  <p v-if="selectedModel.base_model"><span class="font-medium">基础模型:</span> {{ selectedModel.base_model }}</p>
                  <div v-if="selectedModel.tags && selectedModel.tags.length > 0">
                    <span class="font-medium">标签:</span>
                    <div class="mt-2 flex flex-wrap gap-1">
                      <span 
                        v-for="tag in selectedModel.tags" 
                        :key="tag"
                        class="badge badge-neutral"
                      >{{ tag }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-soft btn-secondary" 
              data-overlay="#model-detail-modal"
              @click="closeModelDetail"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 py-6">
      <div class="flex flex-col lg:flex-row">
        <!-- 主内容区 -->
        <div class="flex-1">
          <div v-if="error" class="alert alert-danger" role="alert">
            <span class="icon-[tabler--alert-circle] me-2"></span>
            {{ error }}
          </div>

          <div v-if="loading" class="text-center py-8">
            <div class="w-full mb-4">
              <div class="progress h-5">
                <div 
                  class="progress-bar progress-bar-striped progress-bar-animated" 
                  role="progressbar" 
                  :style="`width: ${progress}%`" 
                  :aria-valuenow="progress" 
                  aria-valuemin="0" 
                  aria-valuemax="100"
                >{{ progress }}%</div>
              </div>
            </div>
            <div class="text-gray-500">{{ progressMessage }}</div>
          </div>

          <!-- 模型列表 -->
          <div v-if="!loading && models.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 pb-8">
            <div v-for="model in filteredModels" :key="model.id">
              <div 
                class="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 cursor-pointer h-full flex flex-col"
                @click="openModelDetails(model)"
              >
                <div class="relative">
                  <img 
                    v-if="model.preview && (nsfw || !model.nsfw)" 
                    :src="model.preview" 
                    class="w-full h-48 object-cover rounded-t-lg" 
                    :alt="model.name">
                  <div 
                    v-else 
                    class="flex items-center justify-center h-48 bg-gray-100 dark:bg-gray-700 rounded-t-lg">
                    <span class="icon-[tabler--photo] size-10 text-gray-400"></span>
                  </div>
                  <div 
                    v-if="model.nsfw" 
                    class="badge badge-danger absolute top-2 right-2"
                  >NSFW</div>
                </div>
                <div class="p-4 flex-1">
                  <h3 class="text-base font-medium truncate">{{ model.name }}</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400 truncate mt-1">{{ model.filename }}</p>
                </div>
                <div class="flex justify-between items-center px-4 py-2 border-t border-gray-100 dark:border-gray-700 text-xs text-gray-500">
                  <span>{{ model.type }}</span>
                  <span v-if="model.size">{{ formatFileSize(model.size) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div class="flex flex-col items-center justify-center py-16" v-if="!loading && models.length === 0">
            <div class="text-center">
              <div class="text-center mb-4">
                <span class="icon-[tabler--database-x] text-gray-300 text-6xl"></span>
              </div>
              <h4 class="text-lg font-medium mb-2">未找到模型</h4>
              <p class="text-gray-500 mb-4">请在设置中选择模型目录并进行扫描</p>
              <button 
                type="button"
                class="btn btn-primary"
                @click="openSettings"
              >
                <span class="icon-[tabler--settings] inline-block me-1.5 size-4"></span>
                打开设置
              </button>
            </div>
          </div>
        </div>

        <!-- 侧边栏 -->
        <div 
          v-if="models.length > 0" 
          class="hidden lg:block w-1/4 border-l border-gray-200 dark:border-gray-700 pl-6 bg-gray-50 dark:bg-gray-800"
        >
          <div class="sticky top-20 h-[calc(100vh-5rem)] overflow-y-auto">
            <div class="pb-3 mb-3 border-b border-gray-200 dark:border-gray-700">
              <span class="text-lg font-medium">筛选器</span>
            </div>
            <!-- 筛选器容器 -->
            <div>
              <div v-for="(filter, key) in filters" :key="key" class="mb-6">
                <h6 class="text-base font-medium mb-2">{{ filter.label }}</h6>
                <div class="space-y-2">
                  <div v-for="option in filter.options" :key="option.value" class="flex items-center gap-2">
                    <input 
                      type="checkbox" 
                      class="checkbox checkbox-primary" 
                      :id="`filter-${key}-${option.value}`"
                      :value="option.value"
                      v-model="filter.selected"
                    />
                    <label class="label-text text-base" :for="`filter-${key}-${option.value}`">
                      {{ option.label }} ({{ option.count }})
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动端筛选器抽屉 -->
    <button 
      ref="filterSidebarTrigger" 
      type="button" 
      class="hidden" 
      aria-controls="filter-sidebar" 
      data-drawer="#filter-sidebar"
    ></button>

    <div 
      id="filter-sidebar" 
      class="drawer drawer-end"
      role="dialog" 
      aria-modal="true" 
      tabindex="-1"
    >
      <div class="drawer-dialog">
        <div class="drawer-content">
          <div class="drawer-header">
            <h5 class="drawer-title">筛选器</h5>
            <button 
              type="button" 
              class="btn btn-text btn-circle btn-sm" 
              aria-label="关闭" 
              data-drawer="#filter-sidebar"
            >
              <span class="icon-[tabler--x] size-4"></span>
            </button>
          </div>
          <div class="drawer-body">
            <div v-for="(filter, key) in filters" :key="`mobile-${key}`" class="mb-6">
              <h6 class="text-base font-medium mb-2">{{ filter.label }}</h6>
              <div class="space-y-2">
                <div v-for="option in filter.options" :key="`mobile-${option.value}`" class="flex items-center gap-2">
                  <input 
                    type="checkbox" 
                    class="checkbox checkbox-primary" 
                    :id="`mobile-filter-${key}-${option.value}`"
                    :value="option.value"
                    v-model="filter.selected"
                  />
                  <label class="label-text text-base" :for="`mobile-filter-${key}-${option.value}`">
                    {{ option.label }} ({{ option.count }})
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
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
const modelDetailTrigger = ref<HTMLButtonElement | null>(null);
const settingsModalTrigger = ref<HTMLButtonElement | null>(null);
const filterSidebarTrigger = ref<HTMLButtonElement | null>(null);

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

async function selectPath() {
  try {
    modelPath.value = await ModelsAPI.selectModelPath();
  } catch (e) {
    console.error('选择模型目录失败', e);
    error.value = '选择模型目录失败';
  }
}

function openSettings() {
  if (settingsModalTrigger.value) {
    settingsModalTrigger.value.click();
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
  // 触发模态框打开
  if (modelDetailTrigger.value) {
    modelDetailTrigger.value.click();
  }
}

function closeModelDetail() {
  selectedModel.value = null;
}

function formatFileSize(size: number): string {
  if (size < 1024) return size + ' B';
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB';
  if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(2) + ' MB';
  return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString();
}

function openFilterSidebar() {
  if (filterSidebarTrigger.value) {
    filterSidebarTrigger.value.click();
  }
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


