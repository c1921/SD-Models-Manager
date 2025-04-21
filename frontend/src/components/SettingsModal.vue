<template>
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
      <div class="modal-content bg-base-100">
        <div class="modal-header border-b border-base-200">
          <h3 class="modal-title text-base-content">设置</h3>
          <button 
            type="button" 
            class="btn btn-text btn-circle btn-sm absolute end-3 top-3 text-base-content/70 hover:text-base-content" 
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
              class="tab active-tab:tab-active active text-base-content/70 active:text-base-content" 
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
              class="tab active-tab:tab-active text-base-content/70 active:text-base-content" 
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
                  <span class="label-text font-medium text-base-content">模型目录</span>
                </label>
                <div class="flex items-center space-x-2">
                  <input 
                    id="modelPath"
                    type="text" 
                    class="input input-bordered flex-1 bg-base-100 text-base-content" 
                    placeholder="请选择模型目录" 
                    readonly 
                    :value="modelPath"
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
                <h5 class="text-lg font-medium mb-2 text-base-content">SD Models Manager</h5>
                <p class="text-base-content/80 mb-3">版本 <span>{{ appVersion }}</span></p>
                <p class="mb-2">
                  <a href="https://github.com/c1921/SD-Models-Manager" target="_blank" class="text-primary hover:text-primary-focus flex items-center">
                    <span class="icon-[tabler--brand-github] inline-block me-1.5 size-5"></span>
                    GitHub
                  </a>
                </p>
                <p class="text-sm text-base-content/60">MIT 开源许可 - 版权所有 (c) 2025</p>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer border-t border-base-200">
          <button 
            type="button" 
            class="btn btn-outline" 
            data-overlay="#settings-modal"
          >
            关闭
          </button>
          <button 
            type="button" 
            class="btn btn-primary"
            @click="scanModels"
            data-overlay="#settings-modal"
          >
            扫描模型
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineExpose } from 'vue';
import { ModelsAPI } from '../api/models';

// 属性和事件定义
defineProps<{
  appVersion: string;
  modelPath: string;
}>();

const emit = defineEmits<{
  'update:model-path': [path: string];
  'scan-models': [];
}>();

// 方法
async function selectPath() {
  try {
    const path = await ModelsAPI.selectModelPath();
    emit('update:model-path', path);
  } catch (e) {
    console.error('选择模型目录失败', e);
  }
}

function scanModels() {
  emit('scan-models');
}

// 触发器引用
const settingsModalTrigger = ref<HTMLButtonElement | null>(null);

// 对外暴露的方法
function open() {
  if (settingsModalTrigger.value) {
    settingsModalTrigger.value.click();
  }
}

defineExpose({
  open
});
</script> 