<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <nav class="navbar bg-body-secondary navbar-expand-lg sticky-top">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">
          <img src="/favicon.svg" alt="Stable Diffusion 模型管理器" height="26">
        </a>
        
        <button class="btn btn-success ms-auto" @click="toggleNsfw">
          <i class="bi" :class="nsfw ? 'bi-eye-fill' : 'bi-eye-slash-fill'"></i>
          <span class="ms-1">NSFW {{ nsfw ? '已开启' : '已关闭' }}</span>
        </button>

        <button class="btn ms-3" data-bs-toggle="modal" data-bs-target="#settingsModal">
          <i class="bi bi-gear"></i>
        </button>

        <button class="btn ms-3" @click="toggleDarkMode">
          <i class="bi" :class="darkMode ? 'bi-moon-stars-fill' : 'bi-sun-fill'"></i>
        </button>
        <button class="btn ms-3 d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#filterSidebar">
          <i class="bi bi-funnel-fill"></i>
        </button>
      </div>
    </nav>

    <!-- 设置模态窗 -->
    <div class="modal fade" id="settingsModal" tabindex="-1" aria-labelledby="settingsModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="settingsModalLabel">设置</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <!-- 标签页导航 -->
            <ul class="nav nav-tabs mb-3" id="settingsTabs" role="tablist">
              <li class="nav-item" role="presentation">
                <button class="nav-link active" id="path-tab" data-bs-toggle="tab" data-bs-target="#path-tab-pane" type="button" role="tab">
                  <i class="bi bi-folder2"></i> 路径设置
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button class="nav-link" id="about-tab" data-bs-toggle="tab" data-bs-target="#about-tab-pane" type="button" role="tab">
                  <i class="bi bi-info-circle"></i> 关于
                </button>
              </li>
            </ul>
            
            <!-- 标签页内容 -->
            <div class="tab-content" id="settingsTabContent">
              <!-- 路径设置标签页 -->
              <div class="tab-pane fade show active" id="path-tab-pane" role="tabpanel" tabindex="0">
                <div class="mb-3">
                  <label class="form-label" for="pathInput">模型目录</label>
                  <div class="input-group">
                    <input type="text" class="form-control text-muted" id="pathInput" readonly v-model="modelPath" placeholder="请选择模型目录">
                    <button class="btn btn-outline-secondary" @click="selectPath" type="button">
                      <i class="bi bi-folder2-open"></i> 浏览
                    </button>
                  </div>
                </div>
                <div class="d-flex justify-content-end gap-2 mt-4">
                  <button type="button" class="btn btn-primary" @click="scanModels" data-bs-dismiss="modal">扫描模型</button>
                </div>
              </div>
              
              <!-- 关于标签页 -->
              <div class="tab-pane fade" id="about-tab-pane" role="tabpanel" tabindex="0">
                <div class="text-center py-3">
                  <img src="/favicon.svg" alt="logo" height="64" class="mb-3">
                  <h5>SD Models Manager</h5>
                  <p class="text-muted mb-3">版本 <span>{{ appVersion }}</span></p>
                  <p class="mb-2">
                    <a href="https://github.com/c1921/SD-Models-Manager" target="_blank" class="text-decoration-none">
                      <i class="bi bi-github"></i> GitHub
                    </a>
                  </p>
                  <small class="text-muted">MIT 开源许可 - 版权所有 (c) 2025</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型详情模态框 -->
    <div class="modal fade" id="modelDetailModal" tabindex="-1" aria-labelledby="modelDetailModalLabel">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="modelDetailModalLabel">{{ selectedModel?.name || '' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-8">
                <img v-if="selectedModel?.preview" :src="selectedModel.preview" class="img-fluid rounded" :alt="selectedModel?.name">
                <div v-else class="text-center p-5 bg-body-tertiary rounded">
                  <i class="bi bi-image text-muted" style="font-size: 5rem;"></i>
                  <p class="text-muted mt-3">无预览图</p>
                </div>
              </div>
              <div class="col-md-4">
                <div v-if="selectedModel">
                  <p><strong>文件名:</strong> {{ selectedModel.filename }}</p>
                  <p><strong>模型类型:</strong> {{ selectedModel.type }}</p>
                  <p v-if="selectedModel.size"><strong>文件大小:</strong> {{ formatFileSize(selectedModel.size) }}</p>
                  <p v-if="selectedModel.created_at"><strong>创建时间:</strong> {{ formatDate(selectedModel.created_at) }}</p>
                  <p v-if="selectedModel.hash"><strong>哈希值:</strong> {{ selectedModel.hash }}</p>
                  <p v-if="selectedModel.base_model"><strong>基础模型:</strong> {{ selectedModel.base_model }}</p>
                  <div v-if="selectedModel.tags && selectedModel.tags.length > 0">
                    <strong>标签:</strong>
                    <div class="mt-2">
                      <span v-for="tag in selectedModel.tags" :key="tag" class="badge bg-secondary me-1 mb-1">{{ tag }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container-fluid">
      <div class="row">
        <!-- 主内容区 -->
        <div class="col">
          <div class="container mt-4">
            <div class="alert alert-danger" v-if="error" role="alert">{{ error }}</div>
            <div class="text-center" v-if="loading">
              <div class="progress mb-2" style="height: 20px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated"
                     role="progressbar"
                     :style="`width: ${progress}%`"
                     :aria-valuenow="progress"
                     aria-valuemin="0"
                     aria-valuemax="100">{{ progress }}%</div>
              </div>
              <div class="text-muted">{{ progressMessage }}</div>
            </div>

            <!-- 模型列表 -->
            <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5 g-3 pb-5" v-if="!loading && models.length > 0">
              <div v-for="model in filteredModels" :key="model.id" class="col">
                <div class="card h-100 model-card" @click="openModelDetails(model)">
                  <div class="card-img-top position-relative">
                    <img v-if="model.preview && (nsfw || !model.nsfw)" :src="model.preview" class="card-img-top" :alt="model.name">
                    <div v-else class="text-center p-5 bg-body-tertiary">
                      <i class="bi bi-image text-muted" style="font-size: 3rem;"></i>
                    </div>
                    <span v-if="model.nsfw" class="position-absolute top-0 end-0 badge bg-danger m-2">NSFW</span>
                  </div>
                  <div class="card-body">
                    <h5 class="card-title text-truncate">{{ model.name }}</h5>
                    <p class="card-text text-truncate text-muted">{{ model.filename }}</p>
                  </div>
                  <div class="card-footer d-flex justify-content-between text-muted">
                    <small>{{ model.type }}</small>
                    <small v-if="model.size">{{ formatFileSize(model.size) }}</small>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 空状态 -->
            <div class="text-center py-5" v-if="!loading && models.length === 0">
              <div class="mb-3">
                <i class="bi bi-database-x text-muted" style="font-size: 4rem;"></i>
              </div>
              <h4>未找到模型</h4>
              <p class="text-muted">请在设置中选择模型目录并进行扫描</p>
              <button class="btn btn-primary mt-3" data-bs-toggle="modal" data-bs-target="#settingsModal">
                <i class="bi bi-gear me-1"></i> 打开设置
              </button>
            </div>
          </div>
        </div>

        <!-- 侧边栏 -->
        <div class="col-auto border-start bg-body-tertiary d-none d-lg-block" style="width: 25%;" v-if="models.length > 0">
          <div class="d-flex flex-column position-sticky" style="top: 56px; height: calc(100vh - 56px); overflow-y: auto;">
            <div class="d-flex align-items-center pb-3 my-3 border-bottom">
              <span class="fs-5 fw-semibold">筛选器</span>
            </div>
            <!-- 筛选器容器 -->
            <div id="filterContainer">
              <div v-for="(filter, key) in filters" :key="key" class="mb-4">
                <h6>{{ filter.label }}</h6>
                <div class="form-check" v-for="option in filter.options" :key="option.value">
                  <input class="form-check-input" type="checkbox" 
                         :id="`filter-${key}-${option.value}`"
                         :value="option.value"
                         v-model="filter.selected">
                  <label class="form-check-label" :for="`filter-${key}-${option.value}`">
                    {{ option.label }} ({{ option.count }})
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 画布外侧边栏 -->
    <div class="offcanvas offcanvas-end d-lg-none" tabindex="-1" id="filterSidebar" aria-labelledby="filterSidebarLabel">
      <div class="offcanvas-header bg-body-secondary">
        <h5 class="offcanvas-title" id="filterSidebarLabel">筛选器</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" data-bs-target="#filterSidebar" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body">
        <!-- 移动端筛选器容器 -->
        <div>
          <div v-for="(filter, key) in filters" :key="`mobile-${key}`" class="mb-4">
            <h6>{{ filter.label }}</h6>
            <div class="form-check" v-for="option in filter.options" :key="`mobile-${option.value}`">
              <input class="form-check-input" type="checkbox" 
                     :id="`mobile-filter-${key}-${option.value}`"
                     :value="option.value"
                     v-model="filter.selected">
              <label class="form-check-label" :for="`mobile-filter-${key}-${option.value}`">
                {{ option.label }} ({{ option.count }})
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toasts 容器 -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast text-bg-success" ref="scanCompleteToast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header text-bg-success">
          <i class="bi bi-check-circle me-2"></i>
          <strong class="me-auto">扫描完成</strong>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
          所有模型已扫描完成
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch, onUnmounted } from 'vue';
import { Modal, Toast } from 'bootstrap';
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
  document.documentElement.setAttribute('data-bs-theme', darkMode.value ? 'dark' : 'light');
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
          const toastEl = document.getElementById('scanCompleteToast');
          if (toastEl) {
            const toast = new Toast(toastEl);
            toast.show();
          }
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
  const modalEl = document.getElementById('modelDetailModal');
  if (modalEl) {
    const modal = new Modal(modalEl);
    modal.show();
  }
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
  document.documentElement.setAttribute('data-bs-theme', darkMode.value ? 'dark' : 'light');
  
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
</script>

<style scoped>
.model-card {
  cursor: pointer;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  overflow: hidden;
}

.model-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-img-top {
  height: 200px;
  object-fit: cover;
  background-color: #f8f9fa;
}

/* 适配深色模式 */
[data-bs-theme="dark"] .card-img-top {
  background-color: #343a40;
}
</style>
