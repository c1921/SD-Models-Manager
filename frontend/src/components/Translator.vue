<template>
  <div class="card bg-base-100 shadow-md mb-6">
    <div class="card-body p-4">
      <h3 class="card-title text-lg mb-2">
        <i class="icon-[tabler--language] mr-2"></i>
        快速翻译
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="form-control">
          <div class="flex items-center mb-1">
            <label class="label-text font-medium">输入文本</label>
            <div class="ml-2">
              <button 
                class="btn btn-xs" 
                :class="translateDirection ? 'btn-primary' : ''"
                @click="translateDirection = true"
              >
                中→英
              </button>
              <button 
                class="btn btn-xs ml-1" 
                :class="!translateDirection ? 'btn-primary' : ''"
                @click="translateDirection = false"
              >
                英→中
              </button>
            </div>
          </div>
          <textarea 
            class="textarea textarea-bordered w-full h-28" 
            v-model="inputText"
            :placeholder="translateDirection ? '输入中文内容' : 'Enter English content'"
          ></textarea>
        </div>
        <div class="form-control">
          <label class="label-text font-medium mb-1">翻译结果</label>
          <div class="relative">
            <textarea 
              class="textarea textarea-bordered w-full h-28" 
              v-model="outputText"
              readonly
              placeholder="翻译结果将显示在这里"
            ></textarea>
            <button 
              class="btn btn-sm btn-circle absolute right-2 top-2"
              @click="copyToClipboard"
              v-if="outputText"
              title="复制到剪贴板"
            >
              <i class="icon-[tabler--copy]"></i>
            </button>
          </div>
        </div>
      </div>
      <div class="flex justify-end mt-2">
        <button 
          class="btn btn-primary"
          @click="translate"
          :disabled="isTranslating || !inputText"
        >
          <i class="icon-[tabler--language] mr-1.5"></i>
          {{ isTranslating ? '翻译中...' : '翻译' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { PromptsAPI } from '../api/prompts';

export default defineComponent({
  name: 'QuickTranslator',
  
  setup() {
    const inputText = ref('');
    const outputText = ref('');
    const isTranslating = ref(false);
    const translateDirection = ref(false); // false: 英→中, true: 中→英
    
    // 执行翻译
    const translate = async () => {
      if (!inputText.value || isTranslating.value) return;
      
      isTranslating.value = true;
      outputText.value = '';
      
      try {
        const result = await PromptsAPI.translateText(
          inputText.value,
          translateDirection.value // true: 中→英, false: 英→中
        );
        
        if (result && result.translated) {
          outputText.value = result.translated;
        } else {
          outputText.value = '翻译失败: 无法获取翻译结果';
          console.error('翻译结果格式错误', result);
        }
      } catch (error: any) {
        console.error('快速翻译失败', error);
        outputText.value = `翻译失败: ${error.message || '未知错误'}`;
      } finally {
        isTranslating.value = false;
      }
    };
    
    // 复制到剪贴板
    const copyToClipboard = () => {
      if (!outputText.value) return;
      
      navigator.clipboard.writeText(outputText.value)
        .then(() => {
          console.log('复制到剪贴板成功');
        })
        .catch(err => {
          console.error('复制到剪贴板失败', err);
        });
    };
    
    return {
      inputText,
      outputText,
      isTranslating,
      translateDirection,
      translate,
      copyToClipboard
    };
  }
});
</script> 