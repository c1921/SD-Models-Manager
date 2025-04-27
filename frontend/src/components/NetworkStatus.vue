<template>
  <!-- 网络状态指示器 -->
  <div class="tooltip [--trigger:focus] [--interaction:true]">
    <div class="tooltip-toggle">
      <!-- 状态指示器按钮 -->
      <button 
        type="button" 
        class="flex items-center gap-1 px-2 py-1 rounded-md text-sm"
        title="网络连接状态"
      >
        <div class="inline-grid *:[grid-area:1/1]" v-if="overallStatus === 'success'">
          <div class="status status-success animate-ping opacity-75"></div>
          <div class="status status-success"></div>
        </div>
        <div class="status status-error" v-else-if="overallStatus === 'error'"></div>
        <div class="status status-warning" v-else-if="overallStatus === 'warning'"></div>
        <div class="status status-unknown" v-else></div>
        <span 
          :class="{
            'text-success': overallStatus === 'success',
            'text-error': overallStatus === 'error',
            'text-warning': overallStatus === 'warning',
            'text-base-content': overallStatus === 'unknown'
          }"
        >网络</span>
      </button>
      
      <!-- 状态详情弹出层 -->
      <div class="tooltip-content tooltip-shown:opacity-100 tooltip-shown:visible" role="popover">
        <div class="tooltip-body bg-base-300 rounded-lg p-4 text-start">
          <span v-if="isLoading" class="flex items-center gap-2">
            <div class="status status-warning animate-pulse"></div>
            <span class="text-warning">检测中...</span>
          </span>
          <span v-else class="text-base-content text-base font-medium">网络状态</span>
          
          <div class="mt-3" v-if="!isLoading">
            <!-- Civitai状态 -->
            <div 
              class="flex items-center gap-2 mb-2" 
              :title="civitaiStatus?.result?.message || '未知状态'"
            >
              <div class="inline-grid *:[grid-area:1/1]" v-if="civitaiStatus?.result?.available">
                <div class="status status-success animate-ping opacity-75"></div>
                <div class="status status-success"></div>
              </div>
              <div class="status status-error" v-else></div>
              <span 
                :class="{
                  'text-success': civitaiStatus?.result?.available,
                  'text-error': civitaiStatus && !civitaiStatus.result.available,
                }"
              >
                {{ civitaiStatus?.name || 'Civitai API' }}
                <span class="text-xs text-gray-400" v-if="civitaiStatus?.result?.response_time">
                  ({{ civitaiStatus.result.response_time }}ms)
                </span>
              </span>
            </div>
            
            <!-- Google翻译状态 -->
            <div 
              class="flex items-center gap-2" 
              :title="googleTranslateStatus?.result?.message || '未知状态'"
            >
              <div class="inline-grid *:[grid-area:1/1]" v-if="googleTranslateStatus?.result?.available">
                <div class="status status-success animate-ping opacity-75"></div>
                <div class="status status-success"></div>
              </div>
              <div class="status status-error" v-else></div>
              <span 
                :class="{
                  'text-success': googleTranslateStatus?.result?.available,
                  'text-error': googleTranslateStatus && !googleTranslateStatus.result.available,
                }"
              >
                {{ googleTranslateStatus?.name || 'Google 翻译' }}
                <span class="text-xs text-gray-400" v-if="googleTranslateStatus?.result?.response_time">
                  ({{ googleTranslateStatus.result.response_time }}ms)
                </span>
              </span>
            </div>
          </div>
          
          <!-- 刷新按钮 -->
          <div class="mt-3 flex justify-between items-center">
            <button 
              @click="refreshStatus"
              class="btn btn-xs btn-soft flex items-center gap-1"
              :disabled="isLoading"
            >
              <span class="icon-[tabler--refresh] size-4"></span>
              刷新
            </button>
            <span v-if="lastCheckTime" class="text-xs text-gray-400">
              {{ formatLastCheckTime }}
            </span>
          </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { NetworkAPI } from '../api/network';
import type { NetworkTargetStatus } from '../api/network';

const props = withDefaults(defineProps<{
  autoCheck?: boolean; // 是否自动检查状态
}>(), {
  autoCheck: true
});

const emit = defineEmits<{
  'update:status': ['success' | 'warning' | 'error' | 'unknown'];
}>();

// 状态变量
const isLoading = ref(false);
const civitaiStatus = ref<NetworkTargetStatus | null>(null);
const googleTranslateStatus = ref<NetworkTargetStatus | null>(null);
const lastCheckTime = ref<number | null>(null);

// 计算总体网络状态
const overallStatus = computed(() => {
  // 如果正在加载中或者没有状态数据，返回unknown
  if (isLoading.value || (!civitaiStatus.value && !googleTranslateStatus.value)) {
    return 'unknown';
  }

  // 检查是否所有服务都正常
  const allAvailable = 
    civitaiStatus.value?.result?.available === true && 
    googleTranslateStatus.value?.result?.available === true;
  
  // 检查是否所有服务都不可用
  const allUnavailable = 
    civitaiStatus.value?.result?.available === false && 
    googleTranslateStatus.value?.result?.available === false;
  
  if (allAvailable) {
    return 'success';
  } else if (allUnavailable) {
    return 'error';
  } else {
    return 'warning';
  }
});

// 监听状态变化并通知父组件
watch(overallStatus, (newStatus) => {
  emit('update:status', newStatus);
});

// 计算上次检查时间的友好显示
const formatLastCheckTime = computed(() => {
  if (!lastCheckTime.value) return '';
  
  const now = Date.now();
  const diff = now - lastCheckTime.value * 1000; // 转换为毫秒
  
  if (diff < 60000) {
    return '刚刚';
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`;
  } else {
    return `${Math.floor(diff / 3600000)}小时前`;
  }
});

// 检查网络状态
async function checkNetworkStatus(forceRefresh = false) {
  isLoading.value = true;
  try {
    const response = await NetworkAPI.checkStatus(forceRefresh);
    civitaiStatus.value = response.results.civitai;
    googleTranslateStatus.value = response.results.google_translate;
    lastCheckTime.value = response.last_check;
  } catch (e) {
    console.error('获取网络状态失败', e);
  } finally {
    isLoading.value = false;
  }
}

// 刷新状态
function refreshStatus() {
  checkNetworkStatus(true);
}

// 组件挂载时自动检查
onMounted(() => {
  if (props.autoCheck) {
    checkNetworkStatus();
  }
});
</script>

