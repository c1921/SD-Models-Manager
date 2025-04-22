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
            <span class="icon-[tabler--x] size-5"></span>
          </button>
        </div>
        <div class="modal-body p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="md:col-span-2">
              <div v-if="model?.preview" class="overflow-hidden rounded-lg">
                <img 
                  :src="model.preview" 
                  :class="[
                    'w-full transition-all duration-300', 
                    { 'blur-2xl': model.nsfw && blurNsfw }
                  ]" 
                  :alt="model?.name">
              </div>
              <div 
                v-else 
                class="flex flex-col items-center justify-center p-12 rounded-lg bg-base-200">
                <span class="icon-[tabler--photo] size-12 text-base-content/30"></span>
                <p class="mt-3 text-base-content/70">无预览图</p>
              </div>
            </div>
            <div>
              <div v-if="model" class="mt-3">
                <dl class="divide-y divide-base-content/25">
                  <div class="py-3 sm:grid sm:grid-cols-3 sm:gap-4 text-base">
                    <dt class="font-medium text-base-content">文件名</dt>
                    <dd class="mt-1 text-base-content/80 sm:col-span-2 sm:mt-0 break-all">{{ model.filename }}</dd>
                  </div>
                  <div class="py-3 sm:grid sm:grid-cols-3 sm:gap-4 text-base">
                    <dt class="font-medium text-base-content">模型类型</dt>
                    <dd class="mt-1 text-base-content/80 sm:col-span-2 sm:mt-0">{{ model.type }}</dd>
                  </div>
                  <div v-if="model.size" class="py-3 sm:grid sm:grid-cols-3 sm:gap-4 text-base">
                    <dt class="font-medium text-base-content">文件大小</dt>
                    <dd class="mt-1 text-base-content/80 sm:col-span-2 sm:mt-0">{{ formatFileSize(model.size) }}</dd>
                  </div>
                  <div v-if="model.created_at" class="py-3 sm:grid sm:grid-cols-3 sm:gap-4 text-base">
                    <dt class="font-medium text-base-content">创建时间</dt>
                    <dd class="mt-1 text-base-content/80 sm:col-span-2 sm:mt-0">{{ formatDate(model.created_at) }}</dd>
                  </div>
                  <div v-if="model.hash" class="py-3 sm:grid sm:grid-cols-3 sm:gap-4 text-base">
                    <dt class="font-medium text-base-content">哈希值</dt>
                    <dd class="mt-1 text-base-content/80 sm:col-span-2 sm:mt-0 break-all">{{ model.hash }}</dd>
                  </div>
                  <div v-if="model.base_model" class="py-3 sm:grid sm:grid-cols-3 sm:gap-4 text-base">
                    <dt class="font-medium text-base-content">基础模型</dt>
                    <dd class="mt-1 text-base-content/80 sm:col-span-2 sm:mt-0">{{ model.base_model }}</dd>
                  </div>
                  <div v-if="model.tags && model.tags.length > 0" class="py-3 sm:grid sm:grid-cols-3 sm:gap-4 text-base">
                    <dt class="font-medium text-base-content">标签</dt>
                    <dd class="mt-1 text-base-content/80 sm:col-span-2 sm:mt-0">
                      <div class="flex flex-wrap gap-1">
                        <span 
                          v-for="tag in model.tags" 
                          :key="tag"
                          class="badge badge-secondary"
                        >{{ tag }}</span>
                      </div>
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
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
  blurNsfw: boolean;
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