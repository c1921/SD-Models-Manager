<template>
  <div class="px-1">
    <!-- 加载错误提示 -->
    <div v-if="error" class="alert alert-error" role="alert">
      <span class="icon-[tabler--alert-circle] me-2"></span>
      {{ error }}
    </div>

    <!-- 加载进度条 -->
    <div v-if="loading" class="text-center py-8">
      <div class="w-full mb-4">
        <div class="w-full bg-base-200 rounded-full h-2.5">
          <div 
            class="bg-primary h-2.5 rounded-full transition-all duration-300 ease-in-out" 
            :style="`width: ${progress * 100}%`"
          ></div>
        </div>
      </div>
      <div class="text-base-content/80">{{ progressMessage }}</div>
    </div>

    <!-- 模型列表 -->
    <div v-if="!loading && models.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5 pb-8">
      <div v-for="model in filteredModels" :key="model.id">
        <div 
          class="rounded-lg shadow-sm hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 cursor-pointer h-full flex flex-col bg-base-100 border border-base-200"
        >
          <div 
            class="relative pt-[125%] cursor-pointer overflow-hidden rounded-t-lg"
            @click="onModelClick(model)"
          >
            <img 
              v-if="model.preview && (nsfw || !model.nsfw)" 
              :src="model.preview" 
              :class="[
                'absolute inset-0 w-full h-full object-cover transition-all duration-300',
                { 'blur-2xl': model.nsfw && blurNsfw }
              ]" 
              :alt="model.name">
            <div 
              v-else 
              class="absolute inset-0 flex items-center justify-center bg-base-200">
              <span class="icon-[tabler--photo] size-10 text-base-content opacity-50"></span>
            </div>
            <div 
              v-if="model.nsfw" 
              class="badge badge-error absolute top-2 right-2 z-10"
            >NSFW</div>
          </div>
          <div 
            class="p-4 flex-1 cursor-pointer"
            @click="onModelClick(model)"
          >
            <h3 class="text-base font-medium truncate text-base-content">{{ model.name }}</h3>
            <div class="flex flex-col gap-1 mt-2">
              <div class="text-sm text-base-content/80">类型: {{ model.type }}</div>
              <div class="text-sm text-base-content/80">基础模型: {{ model.base_model }}</div>
              <div v-if="model.size" class="text-sm text-base-content/80">大小: {{ formatFileSize(model.size) }}</div>
            </div>
          </div>
          <div class="join w-full">
            <button 
              class="btn btn-sm btn-soft join-item flex-1"
              @click.stop="copyFileName(model.filename)"
              title="复制文件名"
            >
              <span class="icon-[tabler--copy] size-4 me-1"></span>
            </button>
            <button 
              v-if="model.url"
              class="btn btn-sm btn-soft join-item flex-1"
              @click.stop="openModelUrl(model.url)"
              title="访问下载链接"
            >
              <span class="icon-[tabler--external-link] size-4 me-1"></span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="flex flex-col items-center justify-center py-16" v-if="!loading && models.length === 0">
      <div class="text-center">
        <div class="text-center mb-4">
          <span class="icon-[tabler--database-x] text-6xl text-base-content/30"></span>
        </div>
        <h4 class="text-lg font-medium mb-2">未找到模型</h4>
        <p class="mb-4 text-base-content/70">请在设置中选择模型目录并进行扫描</p>
        <button 
          type="button"
          class="btn btn-primary"
          @click="onOpenSettings"
        >
          <span class="icon-[tabler--settings] inline-block me-1.5 size-5"></span>
          打开设置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Model } from '../api/models';
import toast from '../utils/toast';

defineProps<{
  models: Model[];
  filteredModels: Model[];
  loading: boolean;
  progress: number;
  progressMessage: string;
  error: string;
  nsfw: boolean;
  blurNsfw: boolean;
}>();

const emit = defineEmits<{
  'open-settings': [];
  'model-click': [model: Model];
}>();

function onOpenSettings() {
  emit('open-settings');
}

function onModelClick(model: Model) {
  emit('model-click', model);
}

function copyFileName(filename: string) {
  navigator.clipboard.writeText(filename)
    .then(() => {
      toast.success('文件名已复制到剪贴板');
    })
    .catch(err => {
      console.error('复制失败:', err);
      toast.error('复制失败，请手动复制');
    });
}

function openModelUrl(url: string) {
  if (url) {
    window.open(url, '_blank');
    toast.info('正在打开下载链接');
  }
}

function formatFileSize(size: number): string {
  if (size < 1024) return size + ' B';
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB';
  if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(2) + ' MB';
  return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}
</script> 