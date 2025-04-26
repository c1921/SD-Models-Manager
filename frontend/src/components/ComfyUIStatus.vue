<template>
  <!-- ComfyUI状态指示器 -->
  <div 
    class="flex items-center gap-2 px-2 py-1 rounded-md text-sm"
    :title="message"
  >
    <!-- 使用FlyonUI status组件 -->
    <div class="inline-grid *:[grid-area:1/1]" v-if="status === 'running'">
      <div class="status status-success animate-ping opacity-75"></div>
      <div class="status status-success"></div>
    </div>
    <div class="status status-error" v-else-if="status === 'stopped'"></div>
    <div class="status status-warning animate-pulse" v-else></div>
    <span 
      :class="{
        'text-success': status === 'running',
        'text-error': status === 'stopped',
        'text-warning': status === 'unknown'
      }"
    >ComfyUI</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { ModelsAPI } from '../api/models';

const props = withDefaults(defineProps<{
  // 如果父组件不提供这些属性，组件将进行自动检测
  status?: 'running' | 'stopped' | 'unknown';
  message?: string;
  autoCheck?: boolean; // 是否自动检查状态
  checkInterval?: number; // 检查间隔(毫秒)
}>(), {
  status: 'unknown',
  message: '正在检查ComfyUI状态...',
  autoCheck: false,
  checkInterval: 10000 // 默认10秒检查一次
});

const emit = defineEmits<{
  'update:status': ['running' | 'stopped' | 'unknown'];
  'update:message': [string];
}>();

// 内部状态
const internalStatus = ref<'running' | 'stopped' | 'unknown'>(props.status);
const internalMessage = ref(props.message);
let statusInterval: number | null = null;

// 检查ComfyUI状态
async function checkStatus() {
  try {
    const result = await ModelsAPI.checkComfyUIStatus();
    internalStatus.value = result.status;
    internalMessage.value = result.message;
    
    // 通知父组件状态变化
    emit('update:status', internalStatus.value);
    emit('update:message', internalMessage.value);
  } catch (e) {
    console.error('获取ComfyUI状态失败', e);
    internalStatus.value = 'unknown';
    internalMessage.value = '无法获取ComfyUI状态';
    
    // 通知父组件状态变化
    emit('update:status', internalStatus.value);
    emit('update:message', internalMessage.value);
  }
}

// 监听props变化，同步到内部状态
watch(() => props.status, (newStatus) => {
  internalStatus.value = newStatus;
});

watch(() => props.message, (newMessage) => {
  internalMessage.value = newMessage;
});

// 获取当前展示的状态
const status = computed(() => internalStatus.value);
const message = computed(() => internalMessage.value);

// 生命周期钩子
onMounted(async () => {
  // 如果设置了自动检查
  if (props.autoCheck) {
    // 立即检查一次
    await checkStatus();
    
    // 设定定时器
    statusInterval = window.setInterval(checkStatus, props.checkInterval);
  }
});

// 组件销毁时清理
onUnmounted(() => {
  if (statusInterval !== null) {
    clearInterval(statusInterval);
    statusInterval = null;
  }
});
</script> 