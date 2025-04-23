<template>
  <div class="h-full flex flex-col overflow-hidden">
    <!-- 模型详情模态框组件 -->
    <ModelDetailModal
      ref="modelDetailModalRef"
      :model="selectedModel"
      :blur-nsfw="blurNsfw"
      @close="closeModelDetail"
    />

    <!-- 页面头部工具栏 -->
    <div class="py-3 px-4 sm:px-6 lg:px-8 bg-base-100 border-b border-base-200">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h1 class="text-xl font-semibold">模型管理</h1>
        <div class="flex gap-2">
          <button 
            type="button"
            :class="[
              'btn', 
              nsfw ? 'btn-error' : 'btn-outline',
              'btn-sm md:btn-md'
            ]"
            title="NSFW内容控制"
            @click="toggleNsfw"
          >
            <span class="icon-[tabler--eye-off] size-5" v-if="!nsfw"></span>
            <span class="icon-[tabler--eye] size-5" v-else></span>
            <span class="hidden md:inline ml-2">NSFW {{ nsfw ? '已开启' : '已关闭' }}</span>
          </button>

          <button 
            type="button"
            :class="[
              'btn',
              'btn-outline', 
              'btn-sm md:btn-md',
              blurNsfw ? '' : 'btn-error'
            ]"
            title="NSFW图片模糊控制"
            @click="toggleBlurNsfw"
          >
            <span class="icon-[tabler--blur] size-5" v-if="blurNsfw"></span>
            <span class="icon-[tabler--blur-off] size-5" v-else></span>
            <span class="hidden md:inline ml-2">模糊{{ blurNsfw ? '开' : '关' }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="flex-1 container-fluid flex flex-col lg:flex-row overflow-hidden">
      <!-- 主内容区 - 模型列表组件 -->
      <div class="flex-1 overflow-hidden">
        <div class="h-full overflow-y-auto p-4 md:px-6 md:py-5 bg-base-200">
          <ModelList
            :models="models"
            :filtered-models="filteredModels"
            :loading="loading"
            :progress="progress"
            :progress-message="progressMessage"
            :error="error"
            :nsfw="nsfw"
            :blur-nsfw="blurNsfw"
            @model-click="openModelDetails"
            @model-updated="handleModelUpdated"
          />
        </div>
      </div>

      <!-- 筛选器侧边栏组件 -->
      <FilterSidebar 
        ref="filterSidebarRef"
        :filters="filters"
        :model-count="models.length"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch, onUnmounted } from 'vue';
import { ModelsAPI } from '../api/models';
import type { Model } from '../api/models';
import FilterSidebar from '../components/FilterSidebar.vue';
import ModelList from '../components/ModelList.vue';
import ModelDetailModal from '../components/ModelDetailModal.vue';
import toast from '../utils/toast';

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
const models = ref<Model[]>([]);
const nsfw = ref(false);
const blurNsfw = ref(true);
const loading = ref(false);
const progress = ref(0);
const progressMessage = ref('');
const error = ref('');
const selectedModel = ref<Model | null>(null);
let scanInterval: ReturnType<typeof setInterval> | null = null;

// UI状态控制
const filterSidebarRef = ref<InstanceType<typeof FilterSidebar> | null>(null);
const modelDetailModalRef = ref<InstanceType<typeof ModelDetailModal> | null>(null);

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

function toggleBlurNsfw() {
  blurNsfw.value = !blurNsfw.value;
  // 保存设置到 localStorage
  localStorage.setItem('blurNsfw', String(blurNsfw.value));
}



const scanModels = async () => {
  try {
    // 清除可能的上一个轮询间隔
    if (scanInterval !== null) {
      clearInterval(scanInterval);
      scanInterval = null;
    }
    
    loading.value = true;
    progress.value = 0;
    progressMessage.value = '正在扫描模型...';
    
    const response = await ModelsAPI.scanModels();
    if (!response?.taskId) {
      throw new Error('扫描任务创建失败');
    }

    // 设置轮询间隔
    scanInterval = setInterval(async () => {
      try {
        const status = await ModelsAPI.getScanStatus(response.taskId);
        console.log('轮询获取扫描状态:', status); // 调试日志
        
        // 确保进度值正确传递
        progress.value = status.progress;
        progressMessage.value = status.message;

        if (status.completed) {
          console.log('扫描完成，最终进度:', progress.value); // 调试日志
          if (scanInterval !== null) {
            clearInterval(scanInterval);
            scanInterval = null;
          }
          
          // 短暂延迟以确保用户能看到100%的进度
          setTimeout(async () => {
            loading.value = false;
            await loadModels();
            // 显示扫描完成通知
            toast.success('模型扫描完成');
          }, 500);
        }
      } catch (err) {
        console.error('获取扫描状态失败:', err);
        if (scanInterval !== null) {
          clearInterval(scanInterval);
          scanInterval = null;
        }
        loading.value = false;
        error.value = '获取扫描状态失败';
        // 显示错误通知
        toast.error('扫描状态获取失败');
      }
    }, 500); // 每500ms检查一次状态
  } catch (err) {
    console.error('扫描模型失败:', err);
    loading.value = false;
    error.value = '扫描模型失败';
    // 显示错误通知
    toast.error('扫描模型失败');
  }
};

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

// 处理模型更新
function handleModelUpdated(updatedModel: Model) {
  // 查找并更新模型列表中的对应模型
  const index = models.value.findIndex(model => model.id === updatedModel.id);
  if (index !== -1) {
    models.value[index] = { ...models.value[index], ...updatedModel };
  }
}

// 监听模型列表变化
watch(models, () => {
  updateFilterOptions();
}, { deep: true });

// 生命周期钩子
onMounted(async () => {
  // 添加事件监听器以响应扫描模型事件
  window.addEventListener('scan-models', scanModels);
  
  // 从 localStorage 加载设置
  const savedNsfw = localStorage.getItem('nsfw');
  if (savedNsfw !== null) {
    nsfw.value = savedNsfw === 'true';
  }
  
  // 从 localStorage 加载模糊设置
  const savedBlurNsfw = localStorage.getItem('blurNsfw');
  if (savedBlurNsfw !== null) {
    blurNsfw.value = savedBlurNsfw === 'true';
  }
  
  // 加载模型列表
  loading.value = true;
  await loadModels();
});

// 组件卸载时清理
onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('scan-models', scanModels);
  
  if (scanInterval !== null) {
    clearInterval(scanInterval);
    scanInterval = null;
  }
});
</script> 