<template>
  <div>
    <!-- 加载错误提示 -->
    <div v-if="error" class="alert alert-danger" role="alert">
      <span class="icon-[tabler--alert-circle] me-2"></span>
      {{ error }}
    </div>

    <!-- 加载进度条 -->
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
          @click="onModelClick(model)"
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
          @click="onOpenSettings"
        >
          <span class="icon-[tabler--settings] inline-block me-1.5 size-4"></span>
          打开设置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import type { Model } from '../api/models';

defineProps<{
  models: Model[];
  filteredModels: Model[];
  loading: boolean;
  progress: number;
  progressMessage: string;
  error: string;
  nsfw: boolean;
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

function formatFileSize(size: number): string {
  if (size < 1024) return size + ' B';
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB';
  if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(2) + ' MB';
  return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}
</script> 