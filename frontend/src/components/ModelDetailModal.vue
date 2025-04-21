<template>
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
      <div class="modal-content bg-base-100">
        <div class="modal-header border-b border-base-200">
          <h3 class="modal-title text-base-content">{{ model?.name || '' }}</h3>
          <button 
            type="button" 
            class="btn btn-text btn-circle btn-sm absolute end-3 top-3 text-base-content/70 hover:text-base-content" 
            aria-label="关闭" 
            data-overlay="#model-detail-modal"
            @click="onClose"
          >
            <span class="icon-[tabler--x] size-4"></span>
          </button>
        </div>
        <div class="modal-body">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="md:col-span-2">
              <img 
                v-if="model?.preview" 
                :src="model.preview" 
                class="w-full rounded-lg" 
                :alt="model?.name">
              <div 
                v-else 
                class="flex flex-col items-center justify-center p-12 rounded-lg bg-base-200">
                <span class="icon-[tabler--photo] size-12 text-base-content/30"></span>
                <p class="mt-3 text-base-content/70">无预览图</p>
              </div>
            </div>
            <div>
              <div v-if="model" class="flex flex-col space-y-3 text-base-content">
                <p><span class="font-medium">文件名:</span> {{ model.filename }}</p>
                <p><span class="font-medium">模型类型:</span> {{ model.type }}</p>
                <p v-if="model.size"><span class="font-medium">文件大小:</span> {{ formatFileSize(model.size) }}</p>
                <p v-if="model.created_at"><span class="font-medium">创建时间:</span> {{ formatDate(model.created_at) }}</p>
                <p v-if="model.hash"><span class="font-medium">哈希值:</span> {{ model.hash }}</p>
                <p v-if="model.base_model"><span class="font-medium">基础模型:</span> {{ model.base_model }}</p>
                <div v-if="model.tags && model.tags.length > 0">
                  <span class="font-medium">标签:</span>
                  <div class="mt-2 flex flex-wrap gap-1">
                    <span 
                      v-for="tag in model.tags" 
                      :key="tag"
                      class="badge badge-secondary"
                    >{{ tag }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer border-t border-base-200">
          <button 
            type="button" 
            class="btn btn-outline" 
            data-overlay="#model-detail-modal"
            @click="onClose"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Model } from '../api/models';

defineProps<{
  model: Model | null;
}>();

const emit = defineEmits<{
  'close': [];
}>();

const modelDetailTrigger = ref<HTMLButtonElement | null>(null);

// 打开模态框
function open() {
  if (modelDetailTrigger.value) {
    modelDetailTrigger.value.click();
  }
}

// 关闭模态框
function onClose() {
  emit('close');
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

defineExpose({
  open
});
</script> 